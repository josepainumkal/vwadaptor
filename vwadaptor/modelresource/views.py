import os

import flask
from flask import Blueprint, render_template, request
from flask_login import login_required
from flask import jsonify
from werkzeug import secure_filename
from flask import current_app as app

from flask_restless.helpers import to_dict
from sqlalchemy.inspection import inspect

from vwadaptor.modelrun.models import ModelRun,ModelResource
from vwadaptor.constants import PROGRESS_STATES
from vwadaptor.constants import PROGRESS_STATES_MSG
import json

from flask import send_file

from vwadaptor.helpers import get_relationships_map, generate_file_name
from vwadaptor.modelrun.models import ModelResource


blueprint = Blueprint("modelresource", __name__, url_prefix='/api/modelresources',
                      static_folder="../static")



@blueprint.route("/<int:id>/download",methods=['GET'])
def download_resource(id):
    resource = ModelResource.query.get(id)
    if resource:
      print resource.resource_name
      return send_file(resource.resource_location,attachment_filename=resource.resource_name,as_attachment=True)

@blueprint.route("/download/<string:name>",methods=['GET'])
def download_resource_by_name(name):
    resource = ModelResource.query.filter_by(resource_location=os.path.join(app.config['UPLOAD_FOLDER'],name)).first()
    if resource:
      print resource.resource_name
      return send_file(resource.resource_location,attachment_filename=resource.resource_name,as_attachment=True)

