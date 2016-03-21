from flask.ext.security import SQLAlchemyUserDatastore
from vwadaptor.user.models import User, Role
from .extensions import db

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
