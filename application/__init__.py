import sys

from functools import wraps

from flask import Flask, jsonify, abort, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from flask_reverse_proxy_fix.middleware import ReverseProxyPrefixFix

from .assistant import AssistantManager, OntologyAssistant

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


assistant_manager = AssistantManager()


@jwt.user_claims_loader
def add_claims_to_access_token(user):
	return {"username": user.username, "permission_level": user.permission_level}

@jwt.user_identity_loader
def user_identity_lookup(user):
	return user.username

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
	jti = decrypted_token["jti"]
	return models.RevokedToken.is_jti_blacklisted(jti)
	

def require_level(level):
	def decorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			try:
				verify_jwt_in_request()
				claims = get_jwt_claims()
				
				if claims["permission_level"] < level:
					return {"message": "You do not have enough privileges to access this resource."}, 403
				else:
					return function(*args, **kwargs)
			except Exception as e:
				sys.stderr.write("require_level Exception: {}\n".format(e))
				return {"message": "Unauthorised or expired session. Log in again."}, 403
		
		return wrapper
	return decorator


def view_require_level(level):
	def decorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			try:
				verify_jwt_in_request()
				claims = get_jwt_claims()
				
				if claims["permission_level"] < level:
					flash("You do not have enough privileges to access the requested resource.")
					return redirect(url_for("main.tagging"))
				else:
					return function(*args, **kwargs)
			except Exception as e:
				sys.stderr.write("view_require_level Exception: {}\n".format(e))
				flash("Your session has expired. Please, log in again.")
				return redirect(url_for("main.login"))
		
		return wrapper
	return decorator


def create_app(config="config"):
	app = Flask(__name__, instance_relative_config=False)
	app.config.from_object(config)

	ReverseProxyPrefixFix(app)
	
	db.init_app(app)
	ma.init_app(app)
	jwt.init_app(app)
	migrate = Migrate(app, db)
	
	# Assistants
	ARMAS_ontology = OntologyAssistant("ARMAS", app=app)
	PARTIDOS_ontology = OntologyAssistant("PARTIDOS", app=app)
	assistant_manager.add_assistant(ARMAS_ontology)
	assistant_manager.add_assistant(PARTIDOS_ontology)
	
	with app.app_context():
		# Include routes
		#from . import routes
		
		# Register blueprints
		from application.views import main_bp
		app.register_blueprint(main_bp)
		
		from application.auth import auth_bp
		app.register_blueprint(auth_bp, url_prefix="/api/auth")
		
		from application.api import api_bp
		app.register_blueprint(api_bp, url_prefix="/api")
	
	return app


if __name__ == "__main__":
	app = create_app("config")
	app.run(debug=True)
