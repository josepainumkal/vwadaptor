from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from config import config

db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=db_engine)
# create a Session
db = Session()
