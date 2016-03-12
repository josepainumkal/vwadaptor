import os
import json

import flask
from flask import Blueprint, render_template, request, redirect
from flask_login import login_required
from flask import jsonify
from werkzeug import secure_filename
from flask import current_app as app
from flask import send_file

from flask_restless.helpers import to_dict
from sqlalchemy.inspection import inspect

from vwadaptor.modelrun.models import ModelRun,ModelResource
from vwadaptor.constants import PROGRESS_STATES
from vwadaptor.constants import PROGRESS_STATES_MSG

from vwadaptor.helpers import get_relationships_map, generate_file_name
from vwadaptor.modelrun.models import ModelResource
from vwadaptor.extensions import storage

blueprint = Blueprint("modelresource", __name__, url_prefix='/api/modelresources',
                      static_folder="../static")



@blueprint.route("/<int:id>/download",methods=['GET'])
def download_resource(id):
    resource = ModelResource.query.get(id)
    if resource:
      obj = storage.get(resource.resource_name)
      download_url = obj.download_url()
      return redirect(download_url, code=302)

@blueprint.route("/download/<string:name>",methods=['GET'])
def download_resource_by_name(name):
    resource = ModelResource.query.filter_by(resource_name=name).first()
    if resource:
        obj = storage.get(resource.resource_name)
        download_url = obj.download_url()
        return redirect(download_url, code=302)
