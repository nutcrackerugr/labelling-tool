from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import null

from application.models import *
from application import db, ma, assistant_manager, require_level

from datetime import datetime, timedelta

	
	
class GetTweet(Resource):
	@require_level(1)
	def get(self, tid):
		tweet = None
		
		if tid != 0:
			tweet = Tweet.query.get(tid)
		else:
			username = get_jwt_identity()
			appuser = AppUser.query.filter_by(username=username).scalar()
			annotation = Annotation.query.filter_by(appuser_id=appuser.id).order_by(Annotation.timestamp.desc()).first()

			if annotation:
				tweet = Tweet.query.filter_by(id=annotation.tweet_id).first()
			else:
				tweet = Tweet.query.first()

		
		if tweet:
			return tweet_schema.dump(tweet)
		else:
			return {"error":404, "message":"Not Found"}, 404

class GetAnnotation(Resource):
	@require_level(1)
	def get(self, tid):
		annotation = Annotation.get_last_annotation_for_tweet(tid)

		if annotation:
			return annotation_schema.dump(annotation)
		else:
			return {"error":404, "message":"Not Found"}, 404

class GetAuthorTweets(Resource):
	@require_level(1)
	def get(self, uid, limit=5):
		if uid != 0:
			tweets = Tweet.get_by_user(uid, limit=limit)
		
		if tweets:
			return tweet_schema.dump(tweets, many=True)
		else:
			return {"error":404, "message":"Not Found"}, 404


class CreateTweet(Resource):
	@require_level(7)
	def post(self):
		try:
			data = request.get_json()
			if data:
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
						db.session.add(tweet)
				
				try:
					db.session.commit()
					return {"message": "Tweet created succesfully"}
					
				except:
					return {"message": "Something went wrong", "error": 500}, 500
			
		except:
			return {"message": "Something went wrong. Check your JSON and try again.", "error": 500}, 500


class CreateTweetsFromFile(Resource):
	@require_level(7)
	def get(self, filename):
		try:
			Tweet.create_by_batch_json(filename)
			return {"message": "Tweets created succesfully"}
			
		except:
			return {"message": "Something went wrong", "error": 500}, 500


class CreateTweetsBatch(Resource):
	@require_level(7)
	def post(self):
		try:
			batch = request.get_json()
			if batch:
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
						db.session.add(tweet)
				
				try:
					db.session.commit()
					return {"message": "Tweets created succesfully"}
					
				except:
					return {"message": "Something went wrong", "error": 500}, 500
					
		except Exception as e:
			return {"message": "Something went wrong. Check your JSON and try again.", "error": 500}, 500

class CreateAnnotation(Resource):
	@require_level(1)
	def post(self, tid):
		try:
			data = request.get_json()
			username = get_jwt_identity()

			user = AppUser.query.filter_by(username=username).scalar()

			last_annotation = Annotation.query.filter_by(tweet_id=tid).order_by(Annotation.timestamp.desc()).first()

			if last_annotation.appuser_id == user.id and last_annotation.timestamp + timedelta(minutes=5) > datetime.utcnow():
				last_annotation.timestamp = datetime.utcnow()
				last_annotation.labels = data["labels"]
				last_annotation.highlights = data["highlights"]
				last_annotation.tags = data["tags"]
				last_annotation.comment = data["comment"]
			else:
				a = Annotation(
					tweet_id=tid,
					appuser_id=user.id,
					labels=data["labels"],
					highlights=data["highlights"],
					tags=data["tags"],
					comment=data["comment"]
				)
				user.annotations.append(a)
				db.session.add(a)

			try:
				db.session.commit()
				return {"message": "Annotation created succesfully"}
				
			except:
				return {"message": "Something went wrong", "error": 500}, 500

		except Exception as e:
			print(e)
			return {"message": "Something went wrong. Check your JSON and try again.", "error": 500}, 500


class GetUser(Resource):
	@require_level(1)
	def get(self, uid):
		user = User.query.get(uid)
		return user_schema.dump(user)

class GetLabels(Resource):
	@require_level(1)
	def get(self):
		labels = Label.query.all()
		return label_schema.dump(labels, many=True)

class GetAssistantsSuggestions(Resource):
	@require_level(1)
	def get(self, tid):
		text = db.session.query(Tweet.full_text).filter_by(id=tid).scalar()
		response = assistant_manager.run(text)
		
		return response, 200
