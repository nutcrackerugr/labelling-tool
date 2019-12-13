from flask import Blueprint
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


api_bp = Blueprint("api", __name__)
api = Api(api_bp)

import views, models, login_resources, resources

# Route
api.add_resource(login_resources.UserRegistration,  "/register")
api.add_resource(login_resources.UserLogin,         "/login")
api.add_resource(login_resources.UserLogoutAccess,  "/logout/access")
api.add_resource(login_resources.UserLogoutRefresh, "/logout/refresh")
api.add_resource(login_resources.TokenRefresh,      "/token/refresh")
# ~ api.add_resource(login_resources.AllUsers,          "/users")
# ~ api.add_resource(login_resources.SecretResource,    "/secret")
