from flask import Blueprint, render_template, abort
from flask_jwt_extended import get_jwt_identity

from application import db
from application.models import Annotation, AppUser

from sqlalchemy import func, and_

from . import view_require_level

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def login():
	return render_template("login.html")

@main_bp.route("/review")
@view_require_level(1)
def tagging():
	return render_template("tagging.html")
	
@main_bp.route("/review/<tid>")
@view_require_level(1)
def tagging_specific(tid):
	return render_template("tagging.html", specific_tid=tid)

@main_bp.route("/annotate")
@view_require_level(1)
def rank_tagging():
	return render_template("ranktagging.html")

@main_bp.route("/batchupload")
@view_require_level(7)
def batchupload():
	return render_template("createbatch.html")

@main_bp.route("/myprofile")
@view_require_level(1)
def myprofile():
	username = get_jwt_identity()
	appuser = AppUser.query.filter_by(username=username).scalar()

	maximum_timestamps = db.session.query(Annotation.tweet_id, 
		Annotation.appuser_id, func.max(Annotation.timestamp).label("timestamp")
		).group_by(Annotation.tweet_id).subquery()
	annotations = db.session.query(Annotation).filter_by(appuser_id=appuser.id).join(maximum_timestamps, and_(
		maximum_timestamps.c.tweet_id == Annotation.tweet_id, and_(
			maximum_timestamps.c.appuser_id == Annotation.appuser_id,
			maximum_timestamps.c.timestamp == Annotation.timestamp)
		)).order_by(Annotation.timestamp.desc()).all()
	
	stats = {"total": len(annotations)}


	return render_template("myprofile.html", user=appuser.__dict__, annotations=[a.tweet_id for a in annotations[:100]], stats=stats)

@main_bp.route("/signup")
def signup():
	return render_template("signup.html")

@main_bp.route("/phpinfo")
def teapot():
	abort(418)
