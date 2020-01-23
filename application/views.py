from flask import Blueprint, render_template, abort

from . import api

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def login():
	return render_template("login.html")

@main_bp.route("/tagging")
def tagging():
	return render_template("tagging.html")

@main_bp.route("/signup")
def signup():
	return render_template("signup.html")

@main_bp.route("/phpinfo")
def teapot():
	abort(418)
