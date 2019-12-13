from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

from .assistant import AssistantManager, OntologyAssistant

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

assistant_manager = AssistantManager()
ARMAS_ontology = OntologyAssistant("ARMAS")
PRUEBA_ontology = OntologyAssistant("PRUEBA")
assistant_manager.add_assistant(ARMAS_ontology)
assistant_manager.add_assistant(PRUEBA_ontology)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
	jti = decrypted_token["jti"]
	return auth.models.RevokedToken.is_jti_blacklisted(jti)


def create_app(config="config"):
	app = Flask(__name__, instance_relative_config=False)
	app.config.from_object(config)
	
	db.init_app(app)
	ma.init_app(app)
	jwt.init_app(app)
	
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
