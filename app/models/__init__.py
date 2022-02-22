# make sure all SQL Alchemy models are imported (app.db.__init__) before
# initializing DB otherwise, SQL Alchemy might fail to initialize
# relationships properly for more details:
# https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28

from .file import File
from .user import User
