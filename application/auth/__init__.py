from flask import Blueprint
from flask_restful import Api

from . import auth

auth_bp = Blueprint("auth", __name__)
api = Api(auth_bp)

api.add_resource(auth.UserRegistration,  "/register")
api.add_resource(auth.UserLogin,         "/login")
api.add_resource(auth.UserLogoutAccess,  "/logout/access")
api.add_resource(auth.UserLogoutRefresh, "/logout/refresh")
api.add_resource(auth.TokenRefresh,      "/token/refresh")
api.add_resource(auth.AllUsers,          "/users")
