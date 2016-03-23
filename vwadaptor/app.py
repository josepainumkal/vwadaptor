# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import os

from flask import Flask, render_template
from flask.ext.restless import APIManager
#from flask_restless_swagger import SwagAPIManager as APIManager
from flask.ext.cors import CORS

from vwadaptor.settings import ProdConfig
from vwadaptor.extensions import (
    bcrypt,
    cache,
    db,
    login_manager,
    migrate,
    debug_toolbar,
    storage,
)
from vwadaptor.auth import jwt
from vwadaptor import api, user, modelrun, modelresource
from vwadaptor.user.models import User
from vwadaptor.modelrun.models import ModelRun, ModelResource, ModelProgress

from vwadaptor.helpers import modelresource_serializer, modelrun_serializer,user_serializer
#from vwadaptor.helpers import model_resource_before_delete, model_run_before_delete
from vwadaptor.helpers import model_run_after_get_many

from vwadaptor.preprocessors import modelrun_preprocessors, modelresource_preprocessors

def create_app(config_object=ProdConfig):
    """An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_api(app,db)
    register_errorhandlers(app)
    create_directories(app)
    #enable cors
    CORS(app)
    return app


def register_extensions(app):
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    storage.init_app(app)
    jwt.init_app(app)
    return None

def register_api(app,db):
    db.app = app
    apimanager = APIManager(app, flask_sqlalchemy_db=db)

    apimanager.create_api(ModelRun,
        methods=['GET', 'POST','PUT', 'DELETE'],
        serializer=modelrun_serializer,
        preprocessors=modelrun_preprocessors,
        postprocessors={
            'GET_MANY':[model_run_after_get_many]
        },
        allow_delete_many=False,
        results_per_page=-1
    )

    apimanager.create_api(ModelResource,
        methods=['GET', 'POST','PUT', 'DELETE'],
        serializer=modelresource_serializer,
        preprocessors=modelresource_preprocessors,
        exclude_columns=[],
        allow_delete_many=False
    )

    # apimanager.create_api(ModelProgress,
    #     methods=['GET'],
    #     allow_delete_many=False,
    #     postprocessors={
    #         'GET_MANY':[modelprogress_after_get_many]
    #     }
    # )


def register_blueprints(app):
    app.register_blueprint(modelrun.views.blueprint)
    app.register_blueprint(modelresource.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(api.views.blueprint)
    return None

def create_directories(app):
    pass


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None
