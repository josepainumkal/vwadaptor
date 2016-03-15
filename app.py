import os
import time

from vwadaptor.app import create_app
from vwadaptor.settings import DevConfig, ProdConfig


if os.environ.get("VWADAPTOR_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig
'''This is a temporary fix for allowing docker-compose to work.
As docker-copose doesn't have any mechanism yet for health check of dependent services
This is the only way to wait for postgres and any other container(swift perhaps) to start 
'''
time.sleep(10)
app = create_app(config)
