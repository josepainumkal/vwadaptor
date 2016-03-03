# -*- coding: utf-8 -*-
import os
import getpass
os_env = os.environ


class Config(object):
    SECRET_KEY = os_env.get('VWADAPTOR_SECRET', 'f4b635fae2d5cb1a4587b33e3ce1c89c')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    UPLOAD_FOLDER = os_env.get('VWADAPTOR_UPLOAD_FOLDER',os.path.join(APP_DIR,'vwuploads'))
    CELERY_BROKER_URL = os_env.get('VWADAPTOR_CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os_env.get('VWADAPTOR_CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_WORKER_NAME =  os_env.get('VWADAPTOR_CELERY_WORKER_NAME', 'vwadaptor-worker')
    CELERY_SCALE_MIN =  os_env.get('VWADAPTOR_CELERY_SCALE_MIN', 3)
    CELERY_SCALE_MAX =  os_env.get('VWADAPTOR_CELERY_SCALE_MAX', 10)

class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = os_env.get('VWADAPTOR_DEBUG', False)
    SQLALCHEMY_DATABASE_URI = os_env.get('VWADAPTOR_SQLALCHEMY_DATABASE_URI', 'postgresql://localhost/example') # TODO: Change me
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 1  # For faster tests
    WTF_CSRF_ENABLED = False  # Allows form testing
