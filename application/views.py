from flask import Blueprint, render_template, abort

from . import view_require_level

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def login():
	return render_template("login.html")

@main_bp.route("/tagging")
@view_require_level(1)
def tagging():
	return render_template("tagging.html")

@main_bp.route("/batchupload")
@view_require_level(7)
def batchupload():
	return render_template("createbatch.html")

@main_bp.route("/signup")
def signup():
	return render_template("signup.html")

@main_bp.route("/phpinfo")
def teapot():
	abort(418)
