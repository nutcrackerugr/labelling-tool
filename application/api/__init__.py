from flask import Blueprint
from flask_restful import Api

from . import api

api_bp = Blueprint("api", __name__)
apir = Api(api_bp)

apir.add_resource(api.GetTweet,                        "/tweet/<int:tid>")
apir.add_resource(api.GetNextTweetByRanking,           "/tweet/nextinrank")
apir.add_resource(api.GetAnnotation,                   "/tweet/<int:tid>/annotation")
apir.add_resource(api.CreateAnnotation,                "/tweet/<int:tid>/annotation/create")
apir.add_resource(api.CreateTweet,                     "/tweet/create")
apir.add_resource(api.CreateTweetsBatch,               "/tweet/create/batch")
apir.add_resource(api.CreateTweetsFromFile,            "/tweet/create/file/<string:filename>")
apir.add_resource(api.SearchInText,                    "/tweet/search/<string:q>")
apir.add_resource(api.GetUser,                         "/user/<int:uid>")
apir.add_resource(api.GetAuthorTweets,                 "/user/<int:uid>/tweets/<int:limit>")
apir.add_resource(api.GetUnreviewedUserAnnotation,     "/user/annotation/unreviewed") #POST
apir.add_resource(api.ReviewUserAnnotation,            "/user/annotation/review") #POST
apir.add_resource(api.GetLabels,                       "/labels")
apir.add_resource(api.GetAssistantsSuggestions,        "/tweet/<int:tid>/suggestions")
apir.add_resource(api.TransformAnnotationToMultivalue, "/annotation/transformtomultivalue/<string:label>")
apir.add_resource(api.RepairRetweets,                  "/repair/retweets/<string:filename>")
apir.add_resource(api.RankRetweets,                    "/rank/retweets")
apir.add_resource(api.RankTweetsFirstTime,             "/rank/firsttime")
apir.add_resource(api.RankTrackedAndNegativeUsers,     "/rank/tracked")
apir.add_resource(api.CreateGraph,                     "/graph/create/<string:name>")
apir.add_resource(api.TestWorker,                      "/testworker")
apir.add_resource(api.ExpandProperties,                "/properties/expand/<string:filename>")
apir.add_resource(api.GetStats,                        "/stats")
apir.add_resource(api.GetCompletedTasks,               "/tasks/completed")

