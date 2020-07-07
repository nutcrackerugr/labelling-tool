from application import celery, db
from application.models import Annotation, Tweet, User, UserAnnotation

from sqlalchemy import and_, func

import networkx as nx

import time
from datetime import datetime
from collections import Counter, defaultdict
from copy import deepcopy
from itertools import combinations

import json


@celery.task()
def test_task():
    print("It works!")
    return True

@celery.task()
def create_graph(name = "default", path = ""):
    G = nx.Graph()

    parents = db.session.query(Tweet.parent_tweet).filter_by(is_retweet=True).all()
    parentslist = set(list(zip(*parents))[0])
    
    nodes = set()
    edges = list()
    for rt in parentslist:
        users_involved = db.session.query(Tweet.user_id).filter_by(parent_tweet=rt).all()
        list_users_involved = set(list(zip(*users_involved))[0])

        author = db.session.query(Tweet.user_id).filter_by(id_str=rt).first()
        if author:
            list_users_involved.add(author[0])

        subgraph = []
        for user in list_users_involved:
            node = db.session.query(User.id_str).filter_by(id=user).first()
            if node:
                subgraph.append(node[0])

        nodes.update(subgraph)
        edges.extend(tuple(sorted(combination)) for combination in combinations(subgraph, 2))

    edge_counts = Counter(edge for edge in edges)
    G.add_weighted_edges_from((edge[0][0], edge[0][1], edge[1]) for edge in edge_counts.most_common())

    nx.write_gpickle(G, "{}{}_{}.gpickle".format(path, name, time.strftime("%Y%m%d-%H%M%S")))


@celery.task()
def expand_properties(properties, name = "default", path = "", steps = 1, alpha = .2):
    # Load relations graph
    G = nx.read_gpickle("{}{}".format(path, name))

    # Load last annotation for each tweet
    maximum_timestamps = db.session.query(Annotation.tweet_id, 
        Annotation.appuser_id, func.max(Annotation.timestamp).label("timestamp")
        ).group_by(Annotation.tweet_id).subquery()
    annotations = db.session.query(Annotation).join(maximum_timestamps, and_(
        maximum_timestamps.c.tweet_id == Annotation.tweet_id, and_(
            maximum_timestamps.c.appuser_id == Annotation.appuser_id,
            maximum_timestamps.c.timestamp == Annotation.timestamp)
        )).all()

    # Compute p_direct
    dir_props = defaultdict(lambda : defaultdict(float))
    for annotation in annotations:
        for prop in properties:
            if prop in annotation.labels.keys():
                # Beware: * 2 - 1 expects 2 categories
                dir_props[annotation.tweet.user.id_str][prop] += annotation.labels[prop] * 2 - 1

                # Retweets should also be counted for p_direct as they have the same properties than the original tweet
                users_rt = db.session.query(User.id_str).join(Tweet).filter(Tweet.is_retweet == True).filter(Tweet.parent_tweet == annotation.tweet.id_str).all()
                #users_rt = db.session.query(Tweet.user_id).filter_by(is_retweet=True).filter_by(parent_tweet=annotation.tweet.id_str).all()
                for user in users_rt:
                    # Beware: * 2 - 1 expects 2 categories
                    dir_props[user[0]][prop] += annotation.labels[prop] * 2 - 1

    # Beware: not thread-safe
    ext_props = deepcopy(dir_props)
    ext_props_aux = defaultdict(lambda : defaultdict(float))

    # Compute p_extended
    involved_users = set(dir_props.keys())
    involved_neighbours = set()
    for i in range(steps):
        # Extend involved_users with neighbourhood prior to property expansion
        for user in involved_users:
            edges = G.edges(user)
            if edges:
                involved_neighbours.update(list(zip(*edges))[1])
        
        involved_users.update(involved_neighbours)
        involved_neighbours = set()
        
        # Property expansion
        for user in involved_users:
            edges = G.edges(user)
            if edges:
                neighbourhood = list(zip(*edges))[1]

                for prop in properties:
                    sum_prop = 0
                    pos_count = 0
                    neg_count = 0
                    for neighbour in neighbourhood:
                        if prop in ext_props[neighbour].keys():
                            sum_prop += ext_props[neighbour][prop]
                            pos_count += 1 if ext_props[neighbour][prop] > 0 else 0
                            neg_count += 1 if ext_props[neighbour][prop] < 0 else 0

                    if sum_prop > 0:
                        factor = pos_count / len(neighbourhood)
                    elif sum_prop < 0:
                        factor = neg_count / len(neighbourhood)
                    else:
                        factor = (len(neighbourhood) - pos_count - neg_count) / len(neighbourhood)
                    
                    ext_props_aux[user][prop] = alpha * factor * sum_prop
        
        # Prepare for next iteration
        ext_props = ext_props_aux
        ext_props_aux = defaultdict(lambda : defaultdict(float))

        # Create annotations
        timestamp = datetime.utcnow()
        for uid_str in ext_props.keys():
            current_user = db.session.query(User).filter_by(id_str=uid_str).first()
            
            # If uid_str user only has retweets, automatically confirm the annotation
            confirmed = False if db.session.query(Tweet.id).filter_by(user_id=current_user.id).filter_by(is_retweet=False).first() is not None else True

            ua = UserAnnotation(user_id=current_user.id, appuser_id=0, timestamp=timestamp, extended_labels=dict(ext_props[uid_str]), reviewed=confirmed, reviewed_by=0, decision=1)
            db.session.add(ua)

        try:
            db.session.commit()
            return {"message": "Properties extended successfully"}
        except Exception as e:
            print(e)
            return {"message": "Something went wrong in async task", "error": 500}, 500
