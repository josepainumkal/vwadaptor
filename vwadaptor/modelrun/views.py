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
from vwadaptor.helpers import modelrun_serializer, modelresource_serializer
#from vwadaptor.validators import modelresource_form_schema

from voluptuous import MultipleInvalid

import json
import requests

from vwadaptor.tasks import  run_model_from_id

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

          msg = {"message":"Resource create for model run "+str(id),'resource':modelresource_serializer(resource)}
          return jsonify(msg), 201

  err = {"message":"Erorr Occured"}
  return jsonify(err), 500

@blueprint.route("/<int:id>/upload/fromurl",methods=['POST'])
#@login_required
def upload_from_url(id):
  '''
    expects json. expects url,filename,resource_type
  '''
  modelrun = ModelRun.query.get(id)
  if modelrun:
    if modelrun.progress_state==PROGRESS_STATES['NOT_STARTED']:
      try:
        data = json.loads(request.get_data())
      except ValueError:
        return jsonify({'message':'Please specify valid json'}), 400

      if not ('url' in data and 'resource_type' in data and 'filename' in data):
        return jsonify({'message':'Invalid Input Provided'}), 400

      try:
        filedata = requests.get(data['url'])
        resource_loc = os.path.join(app.config['UPLOAD_FOLDER'], data['filename'])
        resource_loc =  os.path.join(app.config['UPLOAD_FOLDER'], generate_file_name(resource_loc))
        with app.open_instance_resource(resource_loc, 'wb') as f:
            f.write(filedata.content)
        resource_size = os.stat(resource_loc).st_size
        m = {'modelrun_id':id,'resource_type':data['resource_type'],'resource_location':resource_loc,'resource_size':resource_size}
        resource = ModelResource.create(**m)
        return jsonify({'message':"Resource create for model run "+str(id),'resource':modelresource_serializer(resource)}), 201
      except Exception, e:
        print e
        return jsonify({'message':'Couldn\'t get file from url.'}), 400

    else:
        return jsonify({'message':'Uploading resources to new modelrun is permitted only'}), 400
  err = {"message":"Invalid modlerun id supplied"}
  return jsonify(err), 400


@blueprint.route("/<int:id>/start",methods=['PUT'])
#@login_required
def start(id):
    modelrun = ModelRun.query.get(id)
    if modelrun:
      if modelrun.progress_state==PROGRESS_STATES['NOT_STARTED']:
        if modelrun.resources.count():
          modelrun.progress_state = PROGRESS_STATES['QUEUED']
          modelrun = modelrun.update()
          rels = get_relationships_map(ModelRun)
          task = run_model_from_id.delay(id)
          return jsonify({'message':'ModelRun submitted in queue','modelrun':modelrun_serializer(modelrun),'task_id':task.id}), 200
        else:
          error = {'message':'ModelRun {0} has no resources attached'.format(modelrun)}
          return jsonify(error), 400
      else:
        error = {'message':PROGRESS_STATES_MSG[modelrun.progress_state].format(modelrun_id=modelrun.id)}
        return jsonify(error), 400
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
