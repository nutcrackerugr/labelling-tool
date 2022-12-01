import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = b'GENERATE_TOKEN'

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:passwd@host/database?charset=utf8mb4"
SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_SECRET_KEY = "GENERATE_JWT_SECRET"
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
JWT_TOKEN_LOCATION = ["headers", "cookies"]

JWT_ACCESS_COOKIE_PATH = "/"
JWT_REFRESH_COOKIE_PATH = "/api/auth/token/refresh"
JWT_COOKIE_CSRF_PROTECT = True
JWT_CSRF_CHECK_FORM = True

REVERSE_PROXY_PATH = ""

JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=180)

TIMEDELTA_TO_NEW_ANNOTATION = timedelta(minutes=5)
DEFAULT_PAGE_LENGTH = 30


ONTOLOGIES_PATH = basedir + "/ontologies/"
DASHBOARD_PATH = basedir + "/dashboard-data/"

DUMPS_PATH = "dumps/"
GRAPH_PATH = "graph/"
EXTENDABLE_PROPERTIES = ["PP", "Cs", "VOX", "PSOE", "UP"]

REDIS_QUEUE = "nutcracker_tasks_politologos"
REDIS_URL = "redis://USER:PASSWD@HOST:6379"
RQ_TASK_DEFAULT_TIMEOUT = 3600
