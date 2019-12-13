from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, jwt_required

from application import jwt
from .models import AppUser


parser = reqparse.RequestParser()
parser.add_argument("username", help="This field cannot be blank", required=True)
parser.add_argument("password", help="This field cannot be blank", required=True)

class UserRegistration(Resource):
	def post(self):
		data = parser.parse_args()
		
		if AppUser.find_by_username(data["username"]):
			return {"message": "User {} already exists".format(data["username"])}
		
		new_user = AppUser(username=data["username"], password=data["password"])
		
		try:
			new_user.save()
			access_token = create_access_token(identity=data["username"])
			refresh_token = create_refresh_token(identity=data["username"])
			
			return {
				"message": "User {} was created".format(data["username"]),
				"access_token": access_token,
				"refresh_token": refresh_token,
				"exp": datetime.datetime.utcnow() + timedelta(minutes=5)
			}
		
		except:
			return {"message": "There was a problem creating the user {}".format(data["username"])}, 500


class UserLogin(Resource):
	def post(self):
		data = parser.parse_args()
		
		current_user = AppUser.find_by_username(data["username"])
		
		if not current_user:
			return {"message": "User {} does not exist".format(data["username"])}, 401
			
		if current_user.check_password(data["password"]):
			access_token = create_access_token(identity=current_user.username)
			refresh_token = create_refresh_token(identity=current_user.username)
			
			return {
				"message": "Logged in as {}".format(current_user.username),
				"access_token": access_token,
				"refresh_token": refresh_token
			}, 200
		else:
			return {"message": "Invalid credentials"}, 401


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
