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
from vwadaptor.helpers import get_relationships_map, generate_file_name

from wcwave_adaptors import default_vw_client

import json


blueprint = Blueprint("modelrun", __name__, url_prefix='/api/modelruns',
                      static_folder="../static")



@blueprint.route("/<int:id>/upload",methods=['POST'])
#@login_required
def upload(id):
  modelrun = ModelRun.query.get(id)
  if modelrun:
    if modelrun.progress_state==PROGRESS_STATES['NOT_STARTED']:
      file = request.files['file']
      if file:
          filename = secure_filename(file.filename)
          resource_loc = os.path.join(app.config['UPLOAD_FOLDER'], filename)
          resource_loc =  os.path.join(app.config['UPLOAD_FOLDER'], generate_file_name(resource_loc))
          file.save(resource_loc)

          resource_type=request.form['resource_type']
          resource_size = os.stat(resource_loc).st_size
          m = {'modelrun_id':id,'resource_type':resource_type,'resource_location':resource_loc,'resource_size':resource_size}
          resource = ModelResource.create(**m)

          msg = {"message":"Resource create for model run "+str(id),'resource':to_dict(resource,exclude='resource_location')}
          return jsonify(msg), 201

  err = {"message":"Erorr Occured"}
  return jsonify(err), 500
      

@blueprint.route("/<int:id>/start",methods=['PUT'])
#@login_required
def start(id):
    modelrun = ModelRun.query.get(id)
    if modelrun:
      if modelrun.progress_state==PROGRESS_STATES['NOT_STARTED']:
        modelrun.progress_state = PROGRESS_STATES['QUEUED']
        modelrun = modelrun.update()
        rels = get_relationships_map(ModelRun)
        return jsonify(to_dict(modelrun,deep=rels)), 200
      else:
        error = {'message':PROGRESS_STATES_MSG[modelrun.progress_state].format(modelrun_id=modelrun.id)}
        return jsonify(error)
    else:
      err = {"message":"ModelRun {0} Not Found".format(id)}
      return jsonify(err), 404
      

@blueprint.route("/<int:id>/progress")
#@login_required
def progress(id):
    modelrun = ModelRun.query.get(id)
    if modelrun:
      progress = {"modelrun_id":id,"state":modelrun.progress_state,"value":modelrun.progress_value}
      return jsonify(progress)
    else:
      err = {"error":"ModelRun {0} Not Found".format(id)}
      return jsonify(err), 404

