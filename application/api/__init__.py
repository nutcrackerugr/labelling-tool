from flask import Blueprint
from flask_restful import Api

from . import api

api_bp = Blueprint("api", __name__)
apir = Api(api_bp)

apir.add_resource(api.GetTweet,                  "/tweet/<int:tid>")
apir.add_resource(api.GetAnnotation,             "/tweet/<int:tid>/annotation")
apir.add_resource(api.CreateAnnotation,          "/tweet/<int:tid>/annotation/create")
apir.add_resource(api.CreateTweet,               "/tweet/create")
apir.add_resource(api.CreateTweetsBatch,         "/tweet/create/batch")
apir.add_resource(api.GetUser,                   "/user/<int:uid>")
apir.add_resource(api.GetAuthorTweets,           "/user/<int:uid>/tweets/<int:limit>")
apir.add_resource(api.GetLabels,                 "/labels")
apir.add_resource(api.GetAssistantsSuggestions,  "/tweet/<int:tid>/suggestions")
