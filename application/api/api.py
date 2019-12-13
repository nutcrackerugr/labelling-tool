from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from .models import *
from application import db, ma, assistant_manager
	
	
class GetTweet(Resource):
	@jwt_required
	def get(self, tid):
		if tid != 0:
			tweet = Tweet.query.get(tid)
		else:
			tweet = Tweet.query.filter_by(labels=None).first()
		
		if tweet:
			return tweet_schema.dump(tweet)
		else:
			return {"error":404, "message":"Not Found"}, 404

class CreateTweet(Resource):
	@jwt_required
	def post(self):
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
			
			tweet = Tweet(
				id_str=data["id_str"],
				full_text=data["full_text"],
				truncated=data["truncated"],
				created_at=data["created_at"],
				in_reply_to_status_id=data["in_reply_to_status_id_str"],
				in_reply_to_user_id=data["in_reply_to_user_id_str"],
				geo=data["geo"],
				coordinates=data["coordinates"],
				retweet_count=data["retweet_count"],
				favorite_count=data["favorite_count"],
				lang=data["lang"],
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

class UpdateHighlights(Resource):
	@jwt_required
	def post(self, tid):
		data = request.get_json()
	
		t = Tweet.query.get(tid)
		if t:
			t.highlights = data
			try:
				db.session.commit()
				return {"message": "Tweet updated succesfully"}
				
			except:
				return {"message": "Something went wrong", "error":500}, 500
		else:
			return {"error":404, "message":"Not Found"}, 404
			
			
		return jsonify(success=True), 200

class UpdateLabels(Resource):
	@jwt_required
	def post(self, tid):
		data = request.get_json()

		t = Tweet.query.get(tid)
		if t:
			t.labels = data
			try:
				db.session.commit()
				return {"message": "Tweet updated succesfully"}
				
			except:
				return {"message": "Something went wrong", "error":500}, 500
		else:
			return {"error":404, "message":"Not Found"}, 404
			
		return jsonify(success=True), 200

class UpdateTags(Resource):
	@jwt_required
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

class GetUser(Resource):
	@jwt_required
	def get(self, uid):
		user = User.query.get(uid)
		return user_schema.dump(user)

class GetLabels(Resource):
	@jwt_required
	def get(self):
		labels = Label.query.all()
		return label_schema.dump(labels, many=True)

class GetAssistantsSuggestions(Resource):
	@jwt_required
	def get(self, tid):
		text = db.session.query(Tweet.full_text).filter_by(id=tid).scalar()
		response = assistant_manager.run(text)
		
		return response, 200
