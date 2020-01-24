from flask import Blueprint
from flask_restful import Api

from . import api

api_bp = Blueprint("api", __name__)
apir = Api(api_bp)

apir.add_resource(api.GetTweet,                  "/tweet/<int:tid>")
apir.add_resource(api.UpdateHighlights,          "/tweet/<int:tid>/update/highlights")
apir.add_resource(api.UpdateLabels,              "/tweet/<int:tid>/update/labels")
apir.add_resource(api.UpdateTags,                "/tweet/<int:tid>/update/tags")
apir.add_resource(api.UpdateComment,             "/tweet/<int:tid>/update/comment")
apir.add_resource(api.CreateTweet,               "/tweet/create")
apir.add_resource(api.CreateTweetsBatch,         "/tweet/create/batch")
apir.add_resource(api.GetUser,                   "/user/<int:uid>")
apir.add_resource(api.GetLabels,                 "/labels")
apir.add_resource(api.GetAssistantsSuggestions,  "/tweet/<int:tid>/suggestions")
