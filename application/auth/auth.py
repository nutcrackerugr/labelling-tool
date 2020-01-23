from datetime import datetime, timedelta
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, jwt_required

from application import jwt
from .models import AppUser, AppUserSchema, appuser_schema

import re


class UserRegistration(Resource):
	def post(self):
		data = request.get_json()

		if data["password"] != data["password2"]:
			return {"message": "Passwords do not match"}, 400
			
		if len(data["password"]) < 6:
			return {"message": "Passwords needs to have at least 6 characters"}, 400

		if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", data["email"]):
			return {"message": "Invalid email address"}, 400
		
		if AppUser.find_by_username(data["username"]):
			return {"message": "User {} already exists".format(data["username"])}, 400
			
		if AppUser.find_by_email(data["email"]):
			return {"message": "E-mail address {} already exists in our database".format(data["email"])}, 400

		data.pop("password2", None) # Remove password2
		new_user = AppUserSchema().load(data)
		
		try:
			new_user.save()
			return {"message": "User {} was created".format(data["username"])}
		except:
			return {"message": "There was a problem creating the user {}".format(data["username"])}, 500


class UserLogin(Resource):
	def post(self):
		data = request.get_json()
		
		current_user = AppUser.find_by_username(data["username"])
		
		if not current_user:
			return {"message": "Invalid credentials. Check your username and password and try again."}, 401
		
		if current_user.is_authorized():
			if current_user.check_password(data["password"]):
				access_token = create_access_token(identity=current_user.username)
				refresh_token = create_refresh_token(identity=current_user.username)
				
				return {
					"message": "Logged in as {}".format(current_user.username),
					"access_token": access_token,
					"refresh_token": refresh_token
				}, 200
			else:
				return {"message": "Invalid credentials. Check your username and password and try again."}, 401
		else:
			return {"message": "User {} has not been approved by the admin yet. If you think this is a mistake, please contact support.".format(data["username"])}, 401


class UserLogoutAccess(Resource):
	@jwt_required
	def post(self):
		jti = get_raw_jwt()["jti"]
		
		try:
			revoked_token = RevokedToken(jti=jti)
			revoked_token.add()
			
			return {"message": "Access token has been revoked"}
		
		except:
			return {"message": "Something went wrong"}, 500


class UserLogoutRefresh(Resource):
	@jwt_refresh_token_required
	def post(self):
		jti = get_raw_jwt()["jti"]
		
		try:
			revoked_token = RevokedToken(jti=jti)
			revoked_token.add()
			
			return {"message": "Refresh token has been revoked"}
		
		except:
			return {"message": "Something went wrong"}, 500


class TokenRefresh(Resource):
	@jwt_refresh_token_required
	def post(self):
		current_user = get_jwt_identity()
		access_token = create_access_token(identity=current_user)
		return {"access_token": access_token}


class AllUsers(Resource):
	def get(self):
		return AppUser.return_all()
	
	def delete(self):
		return AppUser.delete_all()


class SecretResource(Resource):
	@jwt_required
	def get(self):
		return {"answer": 42}
