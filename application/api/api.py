from flask import request, current_app, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import null, and_
from marshmallow import EXCLUDE

from application.models import *
from application import db, ma, assistant_manager, require_level

from datetime import datetime, timedelta

from application.tasks.tweets import repair_retweets, rank_retweets, rank_tweets_first_time, just_sleep
from application.tasks.relations import test_task, create_graph, expand_properties

import random

from . import api_bp

@api_bp.route("/tweet/", methods=["GET"])
@require_level(1)
def get_tweet_by_rank():
	"""Get a tweet with high importance

	Returns:
		Tweet: Tweet with a high current importance
	"""
	tweets = db.session.query(Tweet).filter(Tweet.rank >= 0).order_by(
		Tweet.rank.desc()).limit(5).all()

	if tweets:
		tweet = random.choice(tweets)

		return jsonify(tweet_schema.dump(tweet))
	else:
		return make_response(jsonify(message="No more tweets"), 404)


@api_bp.route("/tweet/", methods=["POST"])
@require_level(7)
def create_tweet():
	"""Creates a new tweet

	Returns:
		Tweet: Created tweet
	"""
	try:
		data = request.get_json()
		if data:
			u = db.session.query(User).filter_by(id_str=data["user"]["id_str"]).scalar()
			
			if not u:
				if not "user" in data.keys():
					return make_response(jsonify(message="User does not exists and your request does not contain required information"), 400)
				else:
					del data["user"]["id"]
					u = user_schema.load(data["user"], unknown=EXCLUDE)
					db.session.add(u)
			
			tweet = db.session.query(Tweet).filter_by(id_str=data["id_str"]).scalar()
			
			if not tweet:
				if "full_text" in data.keys():
					text = data["full_text"]
				elif "extended_tweet" in data.keys():
					text = data["extended_tweet"]["full_text"]
				else:
					text = data["text"]
		
				if "retweeted_status" in data.keys():
					is_retweet = True
					parent_tweet = data["retweeted_status"]["id_str"]
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
					geo=str(data["geo"]),
					coordinates=str(data["coordinates"]),
					retweet_count=data["retweet_count"],
					favorite_count=data["favorite_count"],
					lang=data["lang"],
					is_retweet=is_retweet,
					parent_tweet=parent_tweet,
					retweeted=data["retweeted"],
					favorited=data["favorited"],
					rank=data["proposed_rank"] if "proposed_rank" in data.keys() else data["retweet_count"] if not is_retweet else -1,
				)
		
				u.tweets.append(tweet)
				db.session.add(tweet)
			
				try:
					db.session.commit()
				except:
					return make_response(jsonify(message="Something went wrong"), 500)
				
			return jsonify(tweet_schema.dump(tweet))
		
	except Exception as e:
		print(e)
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)

@api_bp.route("/tweet/<int:tid>/", methods=["GET"])
@require_level(1)
def get_specific_tweet(tid: int):
	tweet = Tweet.query.get(tid)

	if tweet:
		return jsonify(tweet_schema.dump(tweet))
	else:
		return make_response(jsonify(message="Not found"), 404)

@api_bp.route("/tweet/<int:tid>/annotation/", methods=["GET"])
@require_level(1)
def get_specific_tweet_annotation(tid: int):
	annotation = Annotation.get_last_annotation_for_tweet(tid)

	if annotation:
		return jsonify(annotation_schema.dump(annotation))
	else:
		return make_response(jsonify(message="Not found"), 404)

@api_bp.route("/tweet/<int:tid>/annotation/", methods=["POST"])
@require_level(1)
def create_specific_tweet_annotation(tid: int):
	try:
		data = request.get_json()
		username = get_jwt_identity()

		tweet = Tweet.query.get(tid)
		if tweet.rank > 0 and username != "tracker":
			tweet.rank *= -1

		appuser = AppUser.query.filter_by(username=username).scalar()

		annotation = Annotation.query.filter_by(tweet_id=tid).order_by(
			Annotation.timestamp.desc()).first()

		if annotation and annotation.appuser_id == appuser.id and annotation.timestamp + current_app.config["TIMEDELTA_TO_NEW_ANNOTATION"] > datetime.utcnow():
			annotation.timestamp = datetime.utcnow()
			annotation.labels = data["labels"]
			annotation.highlights = data["highlights"]
			annotation.tags = data["tags"]
			annotation.comment = data["comment"]
		else:
			annotation = annotation_schema.load(data, unknown=EXCLUDE)
			annotation.tweet_id = tweet.id
			annotation.appuser = appuser
			appuser.annotations.append(annotation)
			tweet.annotations.append(annotation)

			db.session.add(annotation)

		try:
			db.session.commit()
			return jsonify(annotation_schema.dump(annotation))
			
		except:
			return make_response(jsonify(message="Something went wrong"), 500)

	except Exception as e:
		import traceback
		traceback.print_stack()
		print(traceback.format_exc())
		return make_response(jsonify(message=f"Something went wrong, please check your request {e} {''.join(traceback.format_stack())}"), 400)

@api_bp.route("/tweet/<int:tid>/suggestions/", methods=["GET"])
@require_level(1)
def get_specific_tweet_suggestions(tid: int):
	details = db.session.query(Tweet.user_id, Tweet.full_text).filter_by(id=tid).first()
	response = assistant_manager.run(*details)
	
	return response, 200

@api_bp.route("/tweet/findByKeywords/", methods=["GET"])
@require_level(1)
def get_tweet_by_keywords():
	try:
		q = request.args["q"]
		page = int(request.args["page"]) if "page" in request.args.keys() else 1
		limit = int(request.args["limit"]) if "limit" in request.args.keys() else current_app.config["DEFAULT_PAGE_LENGTH"]

		words = q.split(" ")
		conditions = [Tweet.full_text.ilike(f"%{word}%") for word in words]
		results = db.session.query(Tweet).filter(and_(*conditions)).order_by(Tweet.id).paginate(page, per_page=limit).items

		return jsonify(tweet_schema.dump(results, many=True))
	except KeyError:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)


@api_bp.route("/tweet/annotations/", methods=["GET"])
@require_level(1)
def get_annotations():
	try:
		tids = db.session.query(Annotation.tweet_id).group_by(Annotation.tweet_id).all()

		todos = []
		for tid in tids:
			todos.append(db.session.query(Annotation).filter(Annotation.tweet_id == tid[0]).order_by(Annotation.timestamp.desc()).first())
		
		return jsonify(annotation_schema.dump(todos, many=True))

		page = int(request.args["page"]) if "page" in request.args.keys() else 1
		limit = int(request.args["limit"]) if "limit" in request.args.keys() else current_app.config["DEFAULT_PAGE_LENGTH"]

		words = q.split(" ")
		conditions = [Tweet.full_text.ilike(f"%{word}%") for word in words]
		results = db.session.query(Tweet).filter(and_(*conditions)).order_by(Tweet.id).paginate(page, per_page=limit).items

		return jsonify(tweet_schema.dump(results, many=True))
	except KeyError:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)


@api_bp.route("/user/", methods=["POST"])
@require_level(7)
def create_user():
	data = request.get_json()

	u = db.session.query(User).filter_by(id_str=data["id_str"]).scalar()
			
	if not u:
		del data["id"]
		u = user_schema.load(data, unknown=EXCLUDE)
		db.session.add(u)
	
		try:
			db.session.commit(u)
		except:
			return make_response(jsonify(message="Something went wrong"), 500)
		
	return jsonify(user_schema.dump(u))

@api_bp.route("/user/<int:uid>/", methods=["GET"])
@require_level(1, clearance=True)
def get_specific_user(uid: int):
	user = User.query.get(uid)

	if user:
		return jsonify(user_schema.dump(user))
	else:
		return make_response(jsonify(message="User not found"), 404)

@api_bp.route("/user/<int:uid>/tweets/", methods=["GET"])
@require_level(1)
def get_tweets_of_specific_user(uid: int):
	page = int(request.args["page"]) if "page" in request.args.keys() else 1
	limit = int(request.args["limit"]) if "limit" in request.args.keys() else current_app.config["DEFAULT_PAGE_LENGTH"]

	tweets = Tweet.get_by_user(uid, limit=limit, page=page)

	if tweets:
		return jsonify(tweet_schema.dump(tweets, many=True))
	else:
		return make_response(jsonify(message="User has no tweets"), 404)

@api_bp.route("/user/<int:uid>/annotation/", methods=["GET"])
@require_level(1)
def get_specific_user_annotation(uid: int):
	ua = UserAnnotation.get_last_annotation_for_user(uid)

	if ua:
		return jsonify(userannotation_schema.dump(ua))
	else:
		return make_response(jsonify(message="User has no annotations"), 404)

@api_bp.route("/userAnnotation/", methods=["POST"])
@api_bp.route("/user/<int:uid>/annotation/", methods=["POST"])
@require_level(7)
def create_specific_user_annotation(uid: int=None):
	try:
		data = request.get_json()
		username = get_jwt_identity()

		user = User.query.get(uid if uid else data["user_id"])
		appuser = AppUser.query.filter_by(username=username).scalar()

		uannotation = userannotation_schema.load(data, partial=True)
		uannotation.appuser = appuser
		uannotation.appuser_id = appuser.id
		uannotation.timestamp = datetime.utcnow()
		
		appuser.user_annotations.append(uannotation)
		#user.annotations.append(uannotation)
		db.session.add(uannotation)

		try:
			db.session.commit()
			return jsonify(userannotation_schema.dump(uannotation))
			
		except:
			return make_response(jsonify(message="Something went wrong"), 500)

	except:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)

@api_bp.route("/userAnnotation/", methods=["GET"])
@require_level(1)
def get_unreviewed_user_annotation():
	claims = get_jwt()
	ua = UserAnnotation.get_last_unreviewed_annotation(appuser_id=claims["user_id"])

	if ua:
		return jsonify(userannotation_schema.dump(ua))
	else:
		return make_response(jsonify(message="There is not any unreviewed User Annotation"), 404)

@api_bp.route("/userAnnotation/<int:uaid>/", methods=["PUT"])
@api_bp.route("/userAnnotation/", methods=["PUT"])
@require_level(1)
def update_user_annotation(uaid: int=None):
	#TODO: change UserAnnotation primary_key to uaid
	try:
		data = request.get_json()
		username = get_jwt_identity()
		decision = int(data["decision"])

		ua = UserAnnotation.query.get((data["user_id"], data["appuser_id"], data["timestamp"]))

		if not ua.reviewed:
			appuser = AppUser.query.filter_by(username=username).scalar()

			if decision == -99:
				ua.reviewed_by = 2 # FIXME: skip function. Assign to admin in a decent way
			else:
				ua.reviewed = True
				ua.decision = decision
				ua.reviewed_by = appuser.id

				if ua.decision == -1:
					for tweet in ua.user.tweets:
						if not tweet.is_retweet:
							tweet.rank = 99999 - abs(tweet.rank) # just to put them over the top without losing the real score
			
			try:
				db.session.commit()
			except:
				return make_response(jsonify(message="Something went wrong"), 500)
			
		else:
			claims = get_jwt()
			if claims["permission_level"] >= 4:
				ua.decision = data["decision"]
				ua.validated = True

				try:
					db.session.commit()
				except:
					return make_response(jsonify(message="Something went wrong"), 500)
			
			elif ua.decision != data["decision"]:
				uaid = f"{ua.user_id},{ua.appuser_id},{ua.timestamp}"
				return make_response(jsonify(message=f"This annotation was already reviewed and it had a different decision. Contact support and provide the following reference: <UserAnnotation:{uaid}>"), 500)

		return jsonify(userannotation_schema.dump(ua))

	except:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)

@api_bp.route("/userAnnotation/findByStatusAndDecision/", methods=["GET"])
@require_level(1)
def get_user_annotation_by_status():
	try:
		# status: reviewed, unreviewed, validated, unvalidated
		# decision: -1, 0, 1

		statuses = request.args.getlist("status")
		decision = request.args.get("decision", None)

		if "unreviewed" in statuses:
			ua = UserAnnotation.get_last_annotation_by_status(reviewed=False)
		elif "reviewed" in statuses:
			ua = UserAnnotation.get_last_annotation_by_status(reviewed=True)
		elif "unvalidated" in statuses:
			ua = UserAnnotation.get_last_annotation_by_status(validated=False, decision=decision)
		elif "validated" in statuses:
			ua = UserAnnotation.get_last_annotation_by_status(validated=True, decision=decision)
		else:
			return make_response(jsonify(message="Something went wrong, please check your request"), 400)
		
		return jsonify(userannotation_schema.dump(ua))

	except KeyError:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)

@api_bp.route("/labels/", methods=["GET"])
@require_level(1)
def get_labels():
	labels = Label.query.order_by(Label.order).all()
	
	if labels:
		return jsonify(label_schema.dump(labels, many=True))
	else:
		return make_response(jsonify(message="There are no labels"), 404)

@api_bp.route("/video/labels/", methods=["GET"])
@require_level(1)
def get_video_labels():
	labels = VideoLabel.query.order_by(VideoLabel.order).all()

	if labels:
		return jsonify(videolabel_schema.dump(labels, many=True))
	else:
		return make_response(jsonify(message="There are no video labels"), 404)

@api_bp.route("/video/<string:name>/annotation/", methods=["POST"])
@require_level(1)
def create_video_annotation(name: str):
	try:
		data = request.get_json()
		username = get_jwt_identity()

		appuser = AppUser.query.filter_by(username=username).scalar()

		va = videoannotation_schema.load(data)
		va.video = name
		va.appuser = appuser
		
		db.session.add(va)
		appuser.video_annotations.append(va)

		try:
			db.session.commit()
			return jsonify(videoannotation_schema.dump(va))

		except:
			return make_response(jsonify(message="Something went wrong"), 500)

	except:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)

@api_bp.route("/video/<string:name>/annotation/<int:vaid>/", methods=["DELETE"])
@require_level(3)
def delete_video_annotation(name: str, vaid: int):
	try:
		VideoAnnotation.query.filter(VideoAnnotation.video == name).filter(VideoAnnotation.id == vaid).delete(synchronize_session='fetch')
		db.session.commit()

		return jsonify(messge="Segment was deleted"), 200
	
	except:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)

@api_bp.route("/video/<string:name>/annotations/", methods=["GET"])
@require_level(1)
def get_video_annotations(name: str):
	page = int(request.args["page"]) if "page" in request.args.keys() else 1
	limit = int(request.args["limit"]) if "limit" in request.args.keys() else current_app.config["DEFAULT_PAGE_LENGTH"]

	vannotations = VideoAnnotation.get_annotations_for_video(name, page=page, limit=limit)

	if vannotations:
		return jsonify(videoannotation_schema.dump(vannotations, many=True))
	else:
		return make_response(jsonify(message="There are no annotations for this video"), 404)

@api_bp.route("/stats/", methods=["GET"])
@require_level(3)
def get_stats():
	claims = get_jwt()
	level = claims["permission_level"]
	if level == 9:
		level += 1 # To ensure superuser sees everything

	stats = {}
	stats["no_tweets"] = db.session.query(Tweet.id).count()
	stats["no_users"] = db.session.query(User.id).count()
	stats["no_annotations"] = db.session.query(Annotation).count()
	stats["total_user_annotations"] = db.session.query(UserAnnotation).count()

	maximum_timestamps = db.session.query(
		UserAnnotation.user_id, 
		UserAnnotation.appuser_id,
		func.max(UserAnnotation.timestamp).label("timestamp")
		).group_by(UserAnnotation.user_id).subquery()
	
	uannotations = db.session.query(UserAnnotation).join(
		maximum_timestamps, and_(
			maximum_timestamps.c.user_id == UserAnnotation.user_id, and_(
				maximum_timestamps.c.appuser_id == UserAnnotation.appuser_id,
				maximum_timestamps.c.timestamp == UserAnnotation.timestamp
				)
			)	
		).count()

	stats["no_user_annotations"] = uannotations

	appusers = db.session.query(AppUser).filter(AppUser.permission_level < level).all()
	appuser_stats = []
	for appuser in appusers:
		maximum_timestamps = db.session.query(Annotation.tweet_id, 
			Annotation.appuser_id, func.max(Annotation.timestamp).label("timestamp")
			).group_by(Annotation.tweet_id).subquery()
		annotations = db.session.query(Annotation).filter_by(appuser_id=appuser.id).join(maximum_timestamps, and_(
			maximum_timestamps.c.tweet_id == Annotation.tweet_id, and_(
				maximum_timestamps.c.appuser_id == Annotation.appuser_id,
				maximum_timestamps.c.timestamp == Annotation.timestamp)
			)).all()

		maximum_timestamps = db.session.query(UserAnnotation.user_id, 
			UserAnnotation.appuser_id, func.max(UserAnnotation.timestamp).label("timestamp")
			).group_by(UserAnnotation.user_id).subquery()
		uannotations = db.session.query(UserAnnotation).filter_by(reviewed_by=appuser.id, reviewed=True).join(maximum_timestamps, and_(
			maximum_timestamps.c.user_id == UserAnnotation.user_id, and_(
				maximum_timestamps.c.appuser_id == UserAnnotation.appuser_id,
				maximum_timestamps.c.timestamp == UserAnnotation.timestamp)
			)).count()

		nonempty_annotations = len(list(filter(lambda a: not a.is_empty(), annotations)))
		
		appuser_stats.append({"reviewed_annotations": uannotations, "annotations": len(annotations), "nonempty_annotations": nonempty_annotations, "username": appuser.username, "name": appuser.name})
	
	stats["users"] = appuser_stats

	maximum_timestamps = db.session.query(UserAnnotation.user_id, 
		UserAnnotation.appuser_id, func.max(UserAnnotation.timestamp).label("timestamp")
		).group_by(UserAnnotation.user_id).subquery()
	failed_annotations = db.session.query(UserAnnotation).filter_by(reviewed=True, decision=-1).join(maximum_timestamps, and_(
		maximum_timestamps.c.user_id == UserAnnotation.user_id, and_(
			maximum_timestamps.c.appuser_id == UserAnnotation.appuser_id,
			maximum_timestamps.c.timestamp == UserAnnotation.timestamp)
		))

	stats["failed_annotations"] = failed_annotations.count()

	return jsonify(stats)

@api_bp.route("/task/runByName/", methods=["GET"])
@require_level(9)
def run_task():
	try:
		name = request.args.get("name", None)

		username = get_jwt_identity()
		appuser = AppUser.query.filter_by(username=username).scalar()

		if name == "relations.expand_properties":
			filename = request.args.get("filename")
			result = appuser.launch_task(name, properties=current_app.config["EXTENDABLE_PROPERTIES"], filename=filename, path=current_app.config["GRAPH_PATH"])
		elif name == "relations.eval_expand_properties":
			filename = request.args.get("filename")
			limit = int(request.args.get("limit"))
			steps = int(request.args.get("steps"))
			result = appuser.launch_task(name, properties=current_app.config["EXTENDABLE_PROPERTIES"], filename=filename, path=current_app.config["GRAPH_PATH"], annotations_limit=limit, steps=steps)
		elif name == "relations.create_graph":
			filename = request.args.get("filename")
			result = appuser.launch_task(name, path=current_app.config["GRAPH_PATH"], filename=filename)
		elif name in ["tweets.just_sleep", "tweets.rank_tweets_first_time", "tweets.reset_rank"]:
			result = appuser.launch_task(name)
		else:
			return make_response(jsonify(message="Something went wrong, please check your request. Is your taks registered?"), 400)
		
		return jsonify(dict(message="Task scheduled successfully", task=result.id)), 201
	except:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)

@api_bp.route("/tasks/", methods=["GET"])
@require_level(7)
def get_tasks():
	username = get_jwt_identity()
	appuser = AppUser.query.filter_by(username=username).scalar()
	tasks = appuser.get_completed_tasks()

	return jsonify(task_schema.dump(tasks, many=True))

@api_bp.route("/tasks/findByStatus", methods=["GET"])
@require_level(7)
def get_tasks_by_status():
	try:
		status = request.args.getlist("status")

		username = get_jwt_identity()
		appuser = AppUser.query.filter_by(username=username).scalar()

		tasks = []
		if "completed" in status:
			tasks.extend(appuser.get_completed_tasks())

		if "scheduled" in status:
			tasks.extend(appuser.get_tasks_in_progress())
		
		if tasks:
			return jsonify(task_schema.dump(tasks, many=True))
		else:
			return make_response(jsonify(message="There are not any tasks"), 404)
	except:
		return make_response(jsonify(message="Something went wrong, please check your request"), 400)