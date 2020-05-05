import datetime
import json
import jwt
import os

from datetime import datetime, timedelta

from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, post_load

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
	parent_tweet = db.Column(db.String(19), unique=True)
	is_retweet = db.Column(db.Boolean)
	retweeted = db.Column(db.Boolean)
	favorited = db.Column(db.Boolean)
	labels = db.Column(db.PickleType, nullable=True)
	highlights = db.Column(db.PickleType, nullable=True)
	tags = db.Column(db.PickleType, nullable=True)
	comment = db.Column(db.Text, nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	annotations = db.relationship("Annotation", backref="tweet", lazy=True)

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

class Annotation(db.Model):
	# ~ id = db.Column(db.Integer, primary_key=True)
	tweet_id = db.Column(db.Integer, db.ForeignKey("tweet.id"), nullable=False, primary_key=True)
	appuser_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False, primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, primary_key=True)
	
	labels = db.Column(db.PickleType, nullable=True)
	highlights = db.Column(db.PickleType, nullable=True)
	tags = db.Column(db.PickleType, nullable=True)
	comment = db.Column(db.Text, nullable=True)

	@classmethod
	def get_last_annotation_for_tweet(cls, tid):
		return Annotation.query.filter_by(tweet_id=tid).order_by(Annotation.timestamp.desc()).first()
	

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

class AppUser(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(256), nullable=False, unique=True)
	password = db.Column(db.String(256), nullable=False)
	email = db.Column(db.String(256))
	authorized = db.Column(db.Boolean, nullable=False, default=False)
	permission_level = db.Column(db.Integer, nullable=False, default=0)
	annotations = db.relationship("Annotation", backref="appuser", lazy=True)
	
	
	def __init__(self, username, password, email=None, authorized=False, permission_level=0):
		self.username = username
		self.password = Bcrypt().generate_password_hash(password).decode()
		
		self.email = email
		self.authorized = authorized
		self.permission_level = permission_level
	
	@classmethod
	def find_by_username(cls, username):
		return cls.query.filter_by(username=username).first()
		
	@classmethod
	def find_by_email(cls, email):
		return cls.query.filter_by(email=email).first()
		
	@classmethod
	def return_all(cls):
		def to_json(x):
			return {"username": x.username, "password": x.password}
		
		return {"users": list(map(lambda x: to_json(x), AppUser.query.all()))}
	
	@classmethod
	def delete_all(cls):
		try:
			num_rows_deleted = db.session.query(cls).delete()
			db.session.commit()
			return {"message": "{} row(s) deleted".format(num_rows_deleted)}
		
		except:
			return {"message": "Something went wrong", "error": 500}
	
	def check_password(self, password):
		return Bcrypt().check_password_hash(self.password, password)
	
	def is_authorized(self):
		return self.authorized
	
	def get_permission_level(self):
		return self.permission_level
	
	def save(self):
		db.session.add(self)
		db.session.commit()
	
	def generate_token(self, user_id):
		try:
			payload = {
				"exp": datetime.utcnow() + timedelta(secons=30),
				"iat": datetime.utcnow(),
				"sub": user_id
			}
			
			jwt_string = jwt.enconde(payload, app.config.get("SECRET"), algorithm="HS256")
			
			return jwt_string
		except Exception as e:
			return {"message": "Something went wrong", "error": 500}
	
	@staticmethod
	def decode_token(token):
		try:
			payload = jwt.decode(token, app.config.get("SECRET"))
			return payload["sub"]
			
		except jwt.ExpiredSignatureError:
			return {"message": "Session expired. Please log in again", "error": 401}
		except jwt.InvalidTokenError:
			return {"message": "Invalid session. Please log in again", "error": 401}


class RevokedToken(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	jti = db.Column(db.String(120))
	
	def add(self):
		db.session.add(self)
		db.session.commit()
		
	@classmethod
	def is_jti_blacklisted(cls, jti):
		query = cls.query.filter_by(jti=jti).first()
		return bool(query)


class AppUserSchema(ma.ModelSchema):
	def make_appuser(self, data, **kwargs):
		return AppUser(**data)
	
	class Meta:
		model = AppUser
		#exclude = ["password"]

class RevokedTokenSchema(ma.ModelSchema):
	class Meta:
		model = RevokedToken

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
		exclude = ["annotations"]

class AnnotationSchema(ma.ModelSchema):
	highlights = fields.List(fields.String(), attribute="highlights")
	aihighlights = fields.List(fields.String())
	tags = fields.List(fields.String(), attribute="tags")
	labels = fields.Dict(keys=fields.String(), values=fields.Integer(), attribute="labels")
	
	class Meta:
		model = Annotation
		datetimeformat = "%d-%m-%Y %H:%M"
	
	appuser = ma.Nested(AppUserSchema(only=("username",)))


	


tweet_schema = TweetSchema()
annotation_schema = AnnotationSchema()
user_schema = UserSchema()
label_schema = LabelSchema()
appuser_schema = AppUserSchema(exclude=["password"])
revokedtoken_schema = RevokedTokenSchema()