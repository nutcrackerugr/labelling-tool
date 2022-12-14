from flask import Blueprint

api_bp = Blueprint("api", __name__)

from . import api

# apir.add_resource(api.GetNextTweetByRanking,                 "/tweet/nextinrank")
# apir.add_resource(api.CreateTweet,                           "/tweet/create")
# apir.add_resource(api.GetTweet,                              "/tweet/<int:tid>")
# apir.add_resource(api.GetAnnotation,                         "/tweet/<int:tid>/annotation")
# apir.add_resource(api.CreateAnnotation,                      "/tweet/<int:tid>/annotation/create")
# TODO: apir.add_resource(api.CreateTweetsBatch,                     "/tweet/create/batch")
# apir.add_resource(api.SearchInText,                          "/tweet/search/<string:q>")
# apir.add_resource(api.GetAssistantsSuggestions,              "/tweet/<int:tid>/suggestions")
# apir.add_resource(api.GetUser,                               "/user/<int:uid>")
# apir.add_resource(api.GetAuthorTweets,                       "/user/<int:uid>/tweets/<int:limit>")
# apir.add_resource(api.GetUserAnnotation,                     "/user/<int:uid>/annotation")
# apir.add_resource(api.GetUnreviewedUserAnnotation,           "/user/annotation/unreviewed")
# apir.add_resource(api.ReviewUserAnnotation,                  "/user/annotation/review") #POST
# apir.add_resource(api.GetUnvalidatedRejectedUserAnnotation,  "/user/annotation/unvalidated/rejected")
# apir.add_resource(api.GetLabels,                             "/labels")
# apir.add_resource(api.GetVideoLabels,                        "/videolabels")
# apir.add_resource(api.CreateVideoAnnotation,                 "/video/<string:name>/annotation/create")
# apir.add_resource(api.RemoveVideoAnnotation,                 "/video/<string:name>/annotation/<int:vaid>/remove")
# apir.add_resource(api.GetVideoAnnotation,                    "/video/<string:name>/annotations")
# apir.add_resource(api.GetStats,                              "/stats")




# apir.add_resource(api.CreateTweetsFromFile,                  "/tweet/create/file/<string:filename>")


# apir.add_resource(api.TransformAnnotationToMultivalue,       "/annotation/transformtomultivalue/<string:label>")
# apir.add_resource(api.RepairRetweets,                        "/repair/retweets/<string:filename>")
# apir.add_resource(api.RankRetweets,                          "/rank/retweets")
# apir.add_resource(api.RankTweetsFirstTime,                   "/rank/firsttime")
# apir.add_resource(api.RankTrackedAndNegativeUsers,           "/rank/tracked")
# apir.add_resource(api.ResetRank,                             "/rank/reset")
# apir.add_resource(api.CreateGraph,                           "/graph/create/<string:name>")
# apir.add_resource(api.TestWorker,                            "/testworker")
# apir.add_resource(api.ExpandProperties,                      "/properties/expand/<string:filename>")
# apir.add_resource(api.GetCompletedTasks,                     "/tasks/completed")

