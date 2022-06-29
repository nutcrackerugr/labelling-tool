from application import db
from application.models import Annotation, Tweet, Task, Label

from collections import Counter
import glob
import os
import random

from flask import current_app
from sqlalchemy import and_

import networkx as nx

from . import rqjob

@rqjob
def upload_tweets_from_file(filename):
    Tweet.create_by_batch_json(filename)
    return {"message": "Tweets created succesfully"}

@rqjob
def repair_retweets(filepath):
    import json

    tweets = json.load(open(filepath, 'r'))

    for tweet in tweets:
        if "retweeted_status" in tweet.keys():
            db_tweet = db.session.query(Tweet).filter_by(id_str=tweet["id_str"]).scalar()
            if db_tweet:
                db_tweet.is_retweet = True
                db_tweet.parent_tweet = tweet["retweeted_status"]["id_str"]
            
    db.session.commit()


@rqjob
def rank_retweets():
    db.session.query(Tweet).filter_by(is_retweet=True).update({Tweet.rank: -1})
    db.session.commit()

    parents = db.session.query(Tweet.parent_tweet).filter_by(is_retweet=True).all()

    if parents:
        ids = set(list(zip(*parents))[0])
        db.session.query(Tweet).filter(Tweet.id_str.in_(ids)).update({Tweet.rank: 1}, synchronize_session="fetch")
    
    db.session.commit()



@rqjob
def rank_tweets_first_time():
    # Set default importance
    db.session.query(Tweet).update({Tweet.rank: 1})

    # Rank negative tweets that are RT (only originals are important)
    db.session.query(Tweet).filter_by(is_retweet=True).update({Tweet.rank: -1})

    # Rank originals from retweets depending on their importance (no. of RT)
    parents = db.session.query(Tweet).filter_by(is_retweet=True).all()

    if parents:
        retweet_count = Counter([parent.parent_tweet for parent in parents])
        
        for id_str, rank in retweet_count.most_common():
            if rank > 1:
                db.session.query(Tweet).filter_by(id_str=id_str).update({Tweet.rank: rank})
    
    # Rank negatively those tweets that are already annotated
    annotations = db.session.query(Annotation.tweet_id).all()
    
    if list(zip(*annotations)):
        already_annotated_ids = list(set(list(zip(*annotations))[0]))
        db.session.query(Tweet).filter(and_(Tweet.id.in_(already_annotated_ids), Tweet.rank > 0)).update({Tweet.rank: -1 * Tweet.rank}, synchronize_session="fetch")

    try:
        db.session.commit()
        return {"message": "Tweets ranked successfully"}
    except Exception as e:
        print(e)
        return {"message": "Something went wrong in async task", "error": 500}, 500



@rqjob
def reset_rank():
    db.session.query(Tweet).update({Tweet.rank: 0})
    
    try:
        db.session.commit()
        return {"message": "Tweets ranked successfully"}
    except Exception as e:
        print(e)
        return {"message": "Something went wrong in async task", "error": 500}, 500


@rqjob
def rank_negative_annotated_tweets():
    # Rank negatively those tweets that are already annotated
    annotations = db.session.query(Annotation.tweet_id).all()
    already_annotated_ids = list(set(list(zip(*annotations))[0]))
    db.session.query(Tweet).filter(and_(Tweet.id.in_(already_annotated_ids), Tweet.rank > 0)).update({Tweet.rank: -1 * Tweet.rank}, synchronize_session="fetch")

    try:
        db.session.commit()
        return {"message": "Tweets ranked successfully"}
    except Exception as e:
        print(e)
        return {"message": "Something went wrong in async task", "error": 500}, 500


@rqjob
def promote_tracked_tweets_and_negative_users():
    list_of_files = glob.glob(f"{current_app.config['DUMPS_PATH']}/*.gpickle")

    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        
        graph = nx.read_gpickle(latest_file)

        # Tracked users: raise one tweet per node
        # Non-positive users: raise all tweets
        tracked = []
        nonpositive = []

        for nxnode in graph:
            node = graph.nodes[nxnode]["user"]

            if node["tweets"]:
                if node["source"]["kind"] == "tracked_retweets_positive":
                        tracked.append(random.sample(node["tweets"], 1))
                elif len(node["positives"]) == 0:
                    nonpositive += random.sample(node["tweets"], min(5, len(node["tweets"])))
        
        nonpositive = random.sample(nonpositive, min(100, len(nonpositive)))
        
        db.session.query(Tweet).filter(and_(Tweet.id_str.in_(tracked), ~Tweet.is_retweet)).update({Tweet.rank: 9999 - Tweet.rank}, synchronize_session="fetch")
        db.session.query(Tweet).filter(and_(Tweet.id_str.in_(nonpositive), ~Tweet.is_retweet)).update({Tweet.rank: 999 - Tweet.rank}, synchronize_session="fetch")

        try:
            db.session.commit()
            return {"message": "Tweets ranked successfully"}
        except Exception as e:
            print(e)
            return {"message": "Something went wrong in async task", "error": 500}, 500


@rqjob
def just_sleep():
    import time
    time.sleep(10)

    return "OK"


@rqjob
def annotate_emotions():
    import json
    from collections import defaultdict, Counter

    with open(f"{current_app.config['TAXONOMIES_PATH']}/emotions/words.json", 'r') as f:
        words = json.load(f)
    
    with open(f"{current_app.config['TAXONOMIES_PATH']}/emotions/regex.json", 'r') as f:
        expressions = json.load(f)

        processed_exprs = defaultdict(lambda: defaultdict(list))
        for label, values in expressions.items():
            for value, exprlist in values.items():
                for expr in exprlist:
                    processed_exprs[label][value].append([e.strip() for e in expr.split("*") if e])
    
    labels = Label.query.all()
    labelmap = {}
    for l in labels:
        labelmap[l.name] = {
            "multiple": l.multiple,
            "values": l.values.split(",")
        }


    tweets = Tweet.query.all()
    
    for t in tweets:
        text = t.full_text

        found = defaultdict(list)
        highlights = []
        comment = ""
        for label, values in words.items():
            for value, terms in values.items():
                for term in terms:
                    if term in text:
                        comment += f"Found {label.upper()}:{value}::{term}\n"
                        found[label].append(value)
                        highlights.append(term)
        
        for label, values in processed_exprs.items():
            for value, exprs in values.items():
                for expr in exprs:
                    last_index = -1

                    for subexpr in expr:
                        i = text.find(subexpr)

                        if i == -1:
                            last_index = -1
                            break
                        elif i > last_index:
                            last_index = i
                    
                    if last_index != -1:
                        found[label].append(value)
                        highlights.extend(expr)
                        comment += f"Found expression for {label.upper()}:{value}::{expr}\n"


        anns = {}
        for key, values in found.items():
            if len(values) > 1 and labelmap[key]["multiple"]:
                anns[key] = [labelmap[key]["values"].index(v) for v in set(values)]
            elif len (values) > 1:
                c = Counter(values).most_common(1)[0][0]
                anns[key] = labelmap[key]["values"].index(c)
            else:
                anns[key] = labelmap[key]["values"].index(values[0])
        
        if anns:
            a = Annotation(
                tweet_id=t.id,
                appuser_id=0,
                labels=anns,
                highlights=list(set(highlights)),
                comment=comment,
                )
            
            db.session.add(a)
        
    try:
        db.session.commit()
        return {"message": "Emotions annotated successfully"}
    except:
        return {"message": "Something went wrong in async task", "error": 500}, 500

