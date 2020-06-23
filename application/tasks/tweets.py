from application import celery, db
from application.models import Annotation, Tweet

from collections import Counter

@celery.task()
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


@celery.task()
def rank_retweets():
    db.session.query(Tweet).filter_by(is_retweet=True).update({Tweet.rank: -1})
    db.session.commit()

    parents = db.session.query(Tweet.parent_tweet).filter_by(is_retweet=True).all()

    if parents:
        ids = set(list(zip(*parents))[0])
        db.session.query(Tweet).filter(Tweet.id_str.in_(ids)).update({Tweet.rank: 1}, synchronize_session="fetch")
    
    db.session.commit()



@celery.task()
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
    already_annotated_ids = list(set(list(zip(*annotations))[0]))
    db.session.query(Tweet).filter(Tweet.id.in_(already_annotated_ids)).update({Tweet.rank: -1 * Tweet.rank}, synchronize_session="fetch")

    try:
        db.session.commit()
        return {"message": "Tweets ranked successfully"}
    except Exception as e:
        print(e)
        return {"message": "Something went wrong in async task", "error": 500}, 500