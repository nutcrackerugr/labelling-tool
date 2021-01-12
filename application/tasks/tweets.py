from application import db
from application.models import Annotation, Tweet, Task

from collections import Counter
import glob
import os
import random

from flask import current_app
from sqlalchemy import and_

import networkx as nx

from . import rqjob

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
        for nxnode in graph:
            node = graph.nodes[nxnode]["user"]

            if node["source"]["kind"] == "tracked_retweets_positive":
                tid = random.choice(node["tweets"])

                tweet = db.session.query(Tweet).filter(Tweet.id == tid).first()

                if tweet:
                    tweet.rank = 9999 - tweet.rank
            elif len(node["positives"]) == 0:
                for tid in random.sample(node["tweets"], min(5, len(node["tweets"]))):
                    tweet = db.session.query(Tweet).filter(Tweet.id == tid).first()

                    if tweet:
                        tweet.rank = 999 - tweet.rank
    
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