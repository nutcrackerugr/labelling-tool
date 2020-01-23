import jwt
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

from application import db, ma



class AppUser(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(256), nullable=False, unique=True)
	password = db.Column(db.String(256), nullable=False)
	email = db.Column(db.String(256))
	authorized = db.Column(db.Boolean, nullable=False)
	permission_level = db.Column(db.Integer, nullable=False)
	
	
	def __init__(self, username, password, email=None):
		self.username = username
		self.password = Bcrypt().generate_password_hash(password).decode()
		
		if email:
			self.email = email
	
	@classmethod
	def find_by_username(cls, username):
		return cls.query.filter_by(username=username).first()
		
	@classmethod
	def return_all(cls):
		def to_json(x):
			return {"username": x.username, "password": x.password}
		
		return {"users": list(map(lambda x: to_json(x), AppUser.query.all()))}
	
	@classmethod
	def delete_all(cls):
		try:
			num_rows_deleted = db.session.query(cls).delete()
			db.session.commit()
			return {"message": "{} row(s) deleted".format(num_rows_deleted)}
		
		except:
			return {"message": "Something went wrong"}
	
	def check_password(self, password):
		return Bcrypt().check_password_hash(self.password, password)
	
	def is_authorized(self):
		return self.authorized
	
	def save(self):
		db.session.add(self)
		db.session.commit()
	
	def generate_token(self, user_id):
		try:
			payload = {
				"exp": datetime.utcnow() + timedelta(minutes=5),
				"iat": datetime.utcnow(),
				"sub": user_id
			}
			
			jwt_string = jwt.enconde(payload, app.config.get("SECRET"), algorithm="HS256")
			
			return jwt_string
		except Exception as e:
			return str(e) #	OJOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
	
	@staticmethod
	def decode_token(token):
		try:
			payload = jwt.decode(token, app.config.get("SECRET"))
			return payload["sub"]
			
		except jwt.ExpiredSignatureError:
			return "Session expired. Please log in again"
		except jwt.InvalidTokenError:
			return "Invalid session. Please log in again"


class RevokedToken(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	jti = db.Column(db.String(120))
	
	def add(self):
		db.session.add(self)
		db.session.commit()
		
	@classmethod
	def is_jti_blacklisted(cls, jti):
		query = cls.query.filter_by(jti=jti).first()
		return bool(query)


class AppUserSchema(ma.ModelSchema):
	class Meta:
		model = AppUser
		exclude = ["password"]

class RevokedTokenSchema(ma.ModelSchema):
	class Meta:
		model = RevokedToken
	


appuser_schema = AppUserSchema()
revokedtoken_schema = RevokedTokenSchema()
