import os
import sys

from functools import wraps

from flask import Flask, jsonify, abort, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from werkzeug.middleware.proxy_fix import ProxyFix

from redis import Redis
from rq import Queue

from .assistant import AssistantManager, OntologyAssistant, ExtendedPropertiesAssistant


class ReverseProxyPrefixFix(object):
	def __init__(self, app: Flask):
			self.app = app.wsgi_app
			self.prefix = None

			if 'REVERSE_PROXY_PATH' in app.config:
				self.prefix = app.config['REVERSE_PROXY_PATH']

			self.app = ProxyFix(self.app)

			app.wsgi_app = self
	
	def __call__(self, environ, start_response):
		if self.prefix is not None:
			environ['SCRIPT_NAME'] = self.prefix
			path_info = environ['PATH_INFO']
			if path_info.startswith(self.prefix):
				environ['PATH_INFO'] = path_info[len(self.prefix):]

		return self.app(environ, start_response)



db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

assistant_manager = AssistantManager()


@jwt.user_claims_loader
def add_claims_to_access_token(user):
	return {
		"username": user.username,
		"permission_level": user.permission_level,
		"clearance": user.clearance,
	}

@jwt.user_identity_loader
def user_identity_lookup(user):
	return user.username

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
	jti = decrypted_token["jti"]
	return models.RevokedToken.is_jti_blacklisted(jti)
	

def require_level(level, clearance=False):
	def decorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			try:
				verify_jwt_in_request()
				claims = get_jwt_claims()

				if claims["permission_level"] < level or (clearance and not claims["clearance"]):
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
					return redirect(url_for("main.rank_tagging"))
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

	app.redis = Redis.from_url(app.config["REDIS_URL"])
	app.task_queue = Queue(name=app.config["REDIS_QUEUE"], connection=app.redis, default_timeout=app.config["RQ_TASK_DEFAULT_TIMEOUT"])

	ReverseProxyPrefixFix(app)
	
	db.init_app(app)
	ma.init_app(app)
	jwt.init_app(app)
	migrate = Migrate(app, db)
	
	# Assistants
	ARMAS_ontology = OntologyAssistant("ARMAS", app=app)
	PARTIDOS_ontology = OntologyAssistant("PARTIDOS", app=app)
	EXTENDED_PROPERTIES_assistant = ExtendedPropertiesAssistant("Extended Properties")
	assistant_manager.add_assistant(ARMAS_ontology)
	assistant_manager.add_assistant(PARTIDOS_ontology)
	assistant_manager.add_assistant(EXTENDED_PROPERTIES_assistant)
	
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

		@app.template_filter('autoversion')
		def autoversion_filter(filename):
			# determining fullpath might be project specific
			fullpath = os.path.join(os.path.dirname(__file__) + "/", filename[1:])
			try:
				timestamp = str(os.path.getmtime(fullpath))
			except OSError:
				return filename
			newfilename = "{0}?v={1}".format(filename, timestamp)
			return newfilename
	
	return app


if __name__ == "__main__":
	app = create_app("config")
	app.run(debug=True)
