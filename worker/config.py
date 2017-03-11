import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from flask_cloudy import Storage

from celery import Celery

from vwadaptor.settings import DevConfig, ProdConfig

if os.environ.get("VWADAPTOR_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig

#import time
#time.sleep(12)
db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=db_engine)
db = Session()


storage_extra = config.STORAGE_EXTRA
storage = Storage(provider=config.STORAGE_PROVIDER, key=config.STORAGE_KEY,
                  secret=config.STORAGE_SECRET, container=config.STORAGE_CONTAINER,
                  allowed_extensions=config.STORAGE_ALLOWED_EXTENSIONS,**storage_extra)



celery= Celery('vwadaptor',
                broker=config.CELERY_BROKER_URL,
                backend=config.CELERY_RESULT_BACKEND,CELERYD_POOL_RESTARTS=True)


celery.conf.update(
    CELERYD_PREFETCH_MULTIPLIER=1,
    CELERY_ACKS_LATE=True,
    CELERY_CREATE_MISSING_QUEUES = True,
    CELERYD_CONCURRENCY = 1
)