# -*- coding: utf-8 -*-
import os
import getpass
import json
from decouple import config, Csv

from flask_cloudy import ALL_EXTENSIONS

def parse(s):
    def isint(s):
        try:
            int(s)
        except:
            return False
        return True
    def isfloat(s):
        try:
            float(s)
        except:
            return False
        return True
    def isbool(s):
        if s.lower() in ['true','false']:
            return True
        return False

    p = dict(item.split(
            "=") for item in s.split(",") if s)
    for k in p:
        if isint(p[k]):
            p[k]=int(p[k])
        if isfloat(p[k]):
            p[k]=float(p[k])
        if isbool(p[k]):
            p[k]=json.loads(p[k].lower())
    return p

class Config(object):
    SECRET_KEY = config('VWADAPTOR_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    # Database
    SQLALCHEMY_DATABASE_URI = config('VWADAPTOR_SQLALCHEMY_DATABASE_URI',
                                     'sqlite:///{0}'.format(os.path.join(PROJECT_ROOT, 'vwadaptor.db')))  # TODO: Change me

    SQLALCHEMY_BINDS = {
        'users': config('VWADAPTOR_USER_DATABASE_URI','sqlite:///{0}'.format('/vwauthdb/vwauth.db'))
    }
    # Storage
    # Can also be S3, GOOGLE_STORAGE, etc...
    STORAGE_PROVIDER = config('VWADAPTOR_STORAGE_PROVIDER', 'LOCAL')
    STORAGE_KEY = config('VWADAPTOR_STORAGE_KEY', '')
    STORAGE_SECRET = config('VWADAPTOR_STORAGE_SECRET', '')
    STORAGE_CONTAINER = config('VWADAPTOR_STORAGE_CONTAINER', os.path.join(
        APP_DIR, 'uploads'))  # a directory path for local, bucket name of cloud
    # VWADAPTOR_STORAGE_SERVER should be a lowercase string of value true/false
    STORAGE_SERVER = config('VWADAPTOR_STORAGE_SERVER', True, cast=bool)
    # The url endpoint to access files on LOCAL provider
    STORAGE_SERVER_URL = config('VWADAPTOR_STORAGE_SERVER_URL', '/files')
    # should be a comma seperated list
    STORAGE_EXTENSIONS = config('VWADAPTOR_STORAGE_EXTENSIONS', '', cast=Csv())
    STORAGE_ALLOWED_EXTENSIONS = ALL_EXTENSIONS + STORAGE_EXTENSIONS
    #STORAGE_EXTRA = config('VWADAPTOR_STORAGE_EXTRA', '', cast=lambda s: dict(item.split(
    #    "=") for item in s.split(",") if s))  # should be a comma seperated list in format: key=value,key2=value2
    STORAGE_EXTRA = config('VWADAPTOR_STORAGE_EXTRA', '',cast=parse)
    # celery worker
    CELERY_BROKER_URL = config(
        'VWADAPTOR_CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = config(
        'VWADAPTOR_CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    # jwt
    JWT_SECRET_KEY = config('VWADAPTOR_JWT_SECRET_KEY','vwplatform')
    JWT_AUTH_HEADER_PREFIX = config('VWADAPTOR_JWT_AUTH_HEADER_PREFIX','JWT')
	
	#for prms conversion tools
    UPLOAD_FOLDER = config('UPLOAD_FOLDER', '/var/www/vwadaptor/vwadaptor/static/uploadFolder')
    DOWNLOAD_FOLDER = config('DOWNLOAD_FOLDER', '/var/www/vwadaptor/vwadaptor/static/downloadFolder')

class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 1  # For faster tests
    WTF_CSRF_ENABLED = False  # Allows form testing
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    STORAGE_CONTAINER =  os.path.join(Config.APP_DIR, 'teststorage')
