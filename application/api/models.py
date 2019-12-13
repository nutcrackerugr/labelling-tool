import jwt
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

from application import db, ma

	

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
	retweeted = db.Column(db.Boolean)
	favorited = db.Column(db.Boolean)
	labels = db.Column(db.PickleType, nullable=True)
	highlights = db.Column(db.PickleType, nullable=True)
	tags = db.Column(db.PickleType, nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

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

class Label(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32), unique=True, nullable=False)

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
