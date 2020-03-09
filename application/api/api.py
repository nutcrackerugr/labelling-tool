from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from sqlalchemy import null

from .models import *
from application import db, ma, assistant_manager, require_level

	
	
class GetTweet(Resource):
	@require_level(1)
	def get(self, tid):
		if tid != 0:
			tweet = Tweet.query.get(tid)
		else:
			tweet = Tweet.query.filter_by(labels=None).first()
		
		if tweet:
			return tweet_schema.dump(tweet)
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


class UpdateHighlights(Resource):
	@require_level(1)
	def post(self, tid):
		data = request.get_json()
	
		t = Tweet.query.get(tid)
		if t:
			t.highlights = data if data else null()
			try:
				db.session.commit()
				return {"message": "Tweet updated succesfully"}
				
			except:
				return {"message": "Something went wrong", "error":500}, 500
		else:
			return {"error":404, "message":"Not Found"}, 404
			
			
		return jsonify(success=True), 200

class UpdateLabels(Resource):
	@require_level(1)
	def post(self, tid):
		data = request.get_json()

		t = Tweet.query.get(tid)
		if t:
			t.labels = data if data else null()
			try:
				db.session.commit()
				return {"message": "Tweet updated succesfully"}
				
			except:
				return {"message": "Something went wrong", "error":500}, 500
		else:
			return {"error":404, "message":"Not Found"}, 404
			
		return jsonify(success=True), 200

class UpdateTags(Resource):
	@require_level(1)
	def post(self, tid):
		data = request.get_json()
	
		t = Tweet.query.get(tid)
		if t:
			t.tags = data
			try:
				db.session.commit()
				return {"message": "Tweet updated succesfully"}
				
			except:
				return {"message": "Something went wrong", "error":500}, 500
		else:
			return {"error":404, "message":"Not Found"}, 404
			
			
		return jsonify(success=True), 200
		
class UpdateComment(Resource):
	@require_level(1)
	def post(self, tid):
		data = request.form["comment"]
	
		t = Tweet.query.get(tid)
		if t:
			t.comment = data
			try:
				db.session.commit()
				return {"message": "Tweet updated succesfully"}
				
			except:
				return {"message": "Something went wrong", "error":500}, 500
		else:
			return {"error":404, "message":"Not Found"}, 404
			
			
		return jsonify(success=True), 200

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
