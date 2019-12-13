from flask import Blueprint, render_template

from . import api

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def login():
	return render_template("login.html")

@main_bp.route("/tagging")
def tagging():
	return render_template("tagging.html")
