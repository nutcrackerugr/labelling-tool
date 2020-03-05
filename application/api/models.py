import jwt
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

from application import db, ma
import os
import json

	

class Tweet(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	id_str = db.Column(db.String(19), unique=True, nullable=False)
	full_text = db.Column(db.Text, nullable=False)
	truncated = db.Column(db.Boolean, nullable=False)
	created_at = db.Column(db.String(30), nullable=False)
	in_reply_to_status_id = db.Column(db.String(19), nullable=True)
	in_reply_to_user_id = db.Column(db.String(19), nullable=True)
	geo = db.Column(db.Text, nullable=True)
	coordinates = db.Column(db.Text, nullable=True)
	retweet_count = db.Column(db.Integer)
	favorite_count = db.Column(db.Integer)
	lang = db.Column(db.String(30), nullable=True)
	parent_tweet = db.Column(db.String(19), unique=True)
	is_retweet = db.Column(db.Boolean)
	retweeted = db.Column(db.Boolean)
	favorited = db.Column(db.Boolean)
	labels = db.Column(db.PickleType, nullable=True)
	highlights = db.Column(db.PickleType, nullable=True)
	tags = db.Column(db.PickleType, nullable=True)
	comment = db.Column(db.Text, nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

	@classmethod
	def get_by_user(cls, uid, limit=None):
		if limit:
			return Tweet.query.filter_by(user_id=uid).limit(limit).all()
		else:
			return Tweet.query.filter_by(user_id=uid).all()
	
	@classmethod
	def create_by_batch_json(cls, filename):
		with open(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/dumps/" + filename, 'r') as jsonfile:
			batch = json.load(jsonfile)

			count = 0
			for data in batch:
				u = db.session.query(User).filter_by(id_str=data["user"]["id_str"]).scalar()
				if not u:
					u = User(
						id_str=data["user"]["id_str"],
						name=data["user"]["name"],
						screen_name=data["user"]["screen_name"],
						location=data["user"]["location"],
						description=data["user"]["description"],
						protected=data["user"]["protected"],
						profile_image_url_https=data["user"]["profile_image_url_https"]
					)
					db.session.add(u)
					
				t = db.session.query(Tweet).filter_by(id_str=data["id_str"]).scalar()
				
				if not t:
					if "full_text" in data.keys():
						text = data["full_text"]
					elif "extended_tweet" in data.keys():
						text = data["extended_tweet"]["full_text"]
					else:
						text = data["text"]
			
					if "retweet_status" in data.keys():
						is_retweet = True
						parent_tweet = data["retweet_status"]["id_str"]
					else:
						is_retweet = False
						parent_tweet = None
					
					tweet = Tweet(
						id_str=data["id_str"],
						full_text=text,
						truncated=data["truncated"],
						created_at=data["created_at"],
						in_reply_to_status_id=data["in_reply_to_status_id_str"],
						in_reply_to_user_id=data["in_reply_to_user_id_str"],
						geo=data["geo"],
						coordinates=data["coordinates"],
						retweet_count=data["retweet_count"],
						favorite_count=data["favorite_count"],
						lang=data["lang"],
						is_retweet=is_retweet,
						parent_tweet=parent_tweet,
						retweeted=data["retweeted"],
						favorited=data["favorited"]
					)
					
					u.tweets.append(tweet)
					count += 1
					db.session.add(tweet)
					print("Added tweet {}".format(tweet.id_str))

					if count % 100 == 0:
						db.session.commit()
						print("Commiting changes...")

			db.session.commit()



class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	id_str = db.Column(db.String(19), unique=True, nullable=False)
	name = db.Column(db.String(100), nullable=False)
	screen_name = db.Column(db.String(100), nullable=False)
	location = db.Column(db.Text, nullable=True)
	description = db.Column(db.Text, nullable=True)
	protected = db.Column(db.Boolean, nullable=False)
	profile_image_url_https = db.Column(db.Text, nullable=True)
	tweets = db.relationship("Tweet", backref="user", lazy=True)

	def get_tweets(self):
		return Tweet.query.join(User).filter(self.id).all()

class Label(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32), unique=True, nullable=False)
	values = db.Column(db.Text, nullable=False)

class LabelSchema(ma.ModelSchema):
	class Meta:
		model = Label

class UserSchema(ma.ModelSchema):
	class Meta:
		model = User
		
class TweetSchema(ma.ModelSchema):
	highlights = fields.List(fields.String(), attribute="highlights")
	aihighlights = fields.List(fields.String())
	tags = fields.List(fields.String(), attribute="tags")
	labels = fields.Dict(keys=fields.String(), values=fields.Integer(), attribute="labels")
	class Meta:
		model = Tweet
		# ~ exclude = ["labels"]
	


tweet_schema = TweetSchema()
user_schema = UserSchema()
label_schema = LabelSchema()
