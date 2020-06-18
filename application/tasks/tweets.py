from application import celery, db
from application.models import Tweet

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


    