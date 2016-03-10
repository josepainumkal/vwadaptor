# -*- coding: utf-8 -*-
import os
import getpass
from flask_cloudy import ALL_EXTENSIONS
os_env = os.environ


class Config(object):
    SECRET_KEY = os_env.get('VWADAPTOR_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

    STORAGE_PROVIDER= 'LOCAL' # Can also be S3, GOOGLE_STORAGE, etc...
    STORAGE_KEY = ''
    STORAGE_SECRET =  ''
    STORAGE_CONTAINER =  os.path.join(APP_DIR,'uploads')  # a directory path for local, bucket name of cloud
    STORAGE_SERVER = True
    STORAGE_SERVER_URL = '/files' # The url endpoint to access files on LOCAL provider
    STORAGE_ALLOWED_EXTENSIONS = ALL_EXTENSIONS + ['nc','control']
class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/example'  # TODO: Change me
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

    STORAGE_PROVIDER= 'LOCAL' # Can also be S3, GOOGLE_STORAGE, etc...
    STORAGE_KEY = ''
    STORAGE_SECRET =  ''
    STORAGE_CONTAINER =  os.path.join(Config.PROJECT_ROOT,'uploads')  # a directory path for local, bucket name of cloud
    STORAGE_SERVER = True
    STORAGE_SERVER_URL = '/download' # The url endpoint to access files on LOCAL provider


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 1  # For faster tests
    WTF_CSRF_ENABLED = False  # Allows form testing
