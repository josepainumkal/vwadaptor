import os
import json
import requests

import flask
from flask import Blueprint, render_template, request, url_for
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
from vwadaptor.extensions import storage
from vwadaptor.preprocessors import modelrun_authorization_required
from vwadaptor.worker import celery
from celery.result import AsyncResult
import celery.states as states

from voluptuous import MultipleInvalid

from vwpy.modelschema import load_schemas

from flask_jwt import jwt_required


blueprint = Blueprint("modelrun", __name__, url_prefix='/api/modelruns',
                      static_folder="../static")



@blueprint.route("/<int:id>/upload", methods=['POST'])
@jwt_required()
@modelrun_authorization_required
def upload(id):
    modelrun = ModelRun.query.get(id)
    if modelrun:
      # if modelrun.progress_state in
      # [PROGRESS_STATES['NOT_STARTED'],PROGRESS_STATES['RUNNING']]:
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            resource_file = storage.upload(file)
            resource_type = request.form['resource_type']
            m = {
                'modelrun_id': id,
                'resource_type': resource_type,
                'resource_name': resource_file.name,
                #'resource_url': url_for('modelresource.download_resource_by_name', name=resource_file.name, _external=True),
                'resource_size': resource_file.size
            }
            resource = ModelResource.create(**m)

            msg = {"message": "Resource create for model run " +
                   str(id), 'resource': modelresource_serializer(resource)}
            return jsonify(msg), 201
        else:
            err = {"message": "File parameter isn't provided"}
            return jsonify(err), 400
    else:
        err = {"message": "Modelrun doesn't exist"}
        return jsonify(err), 404


@blueprint.route("/<int:id>/upload/fromurl", methods=['POST'])
@jwt_required()
@modelrun_authorization_required
def upload_from_url(id):
    '''
      expects json. expects url,filename,resource_type
    '''
    modelrun = ModelRun.query.get(id)
    if modelrun:
        if modelrun.progress_state == PROGRESS_STATES['NOT_STARTED']:
            try:
                data = json.loads(request.get_data())
            except ValueError:
                return jsonify({'message': 'Please specify valid json'}), 400

            if not ('url' in data and 'resource_type' in data and 'filename' in data):
                return jsonify({'message': 'Invalid Input Provided'}), 400

            try:
                filedata = requests.get(data['url'])
                tmp_loc = os.path.join('/tmp/', data['filename'])
                with app.open_instance_resource(tmp_loc, 'wb') as f:
                    f.write(filedata.content)
                resource_file = storage.upload(tmp_loc)
                resource_type = data['resource_type']
                m = {
                    'modelrun_id': id,
                    'resource_type': resource_type,
                    'resource_name': resource_file.name,
                    #'resource_url': url_for('modelresource.download_resource_by_name', name=resource_file.name, _external=True),
                    'resource_size': resource_file.size
                }
                resource = ModelResource.create(**m)
                return jsonify({'message': "Resource create for model run " + str(id), 'resource': modelresource_serializer(resource)}), 201
            except Exception, e:
                return jsonify({'message': 'Couldn\'t get file from url.'}), 400

        else:
            return jsonify({'message': 'Uploading resources to new modelrun is permitted only'}), 400
    err = {"message": "Invalid modlerun id supplied"}
    return jsonify(err), 400



def queue_length():
    r = requests.get("http://192.168.99.100:5555/api/queues/length")
    # print r.status_code, r.headers, r.content
    resp_dict = json.loads(r.content)
    queue_length = int(resp_dict['active_queues'][0]['messages'])
    # print queue_length
    return queue_length


@blueprint.route("/<int:id>/start",methods=['PUT'])
@jwt_required()
@modelrun_authorization_required
def start(id):
    modelrun = ModelRun.query.get(id)
    if modelrun:
      if modelrun.progress_state==PROGRESS_STATES['NOT_STARTED']:
        schemas = load_schemas()
        schema = schemas[modelrun.model_name]
        needed_resources = set(schema['resources']['inputs'].keys())
        available_resources = set([r.resource_type for r in modelrun.resources])
        if needed_resources==available_resources:
          modelrun.progress_state = PROGRESS_STATES['QUEUED']
          # modelrun = modelrun.update()
          
          # from redis import Redis
          # redis = Redis(host='workerdb', port=6379, db=0)
          # # # # default_queue_length = queue_length()
          # default_queue_length = int(redis.llen('celery'))
          # maxRentedModelsAllowed = int(redis.get('MaxRentedModelsAllowed'))
          # currentRentedModels = int(redis.get('CurrentRentedModels'))

          # if default_queue_length>0 and (currentRentedModels < maxRentedModelsAllowed):
          #   task_id = celery.send_task('vwadaptor.run', args=[], kwargs={'modelrun_id':modelrun.id}, queue='rentedQueue')
          #   currentRentedModels = currentRentedModels+1
          #   p = redis.pipeline()
          #   p.set('CurrentRentedModels', currentRentedModels)
          #   p.execute()
          # else:
          #   task_id = celery.send_task('vwadaptor.run', args=[], kwargs={'modelrun_id':modelrun.id})


          task_id = celery.send_task('vwadaptor.run', args=[], kwargs={'modelrun_id':modelrun.id})
          modelrun.task_id = str(task_id)
          modelrun = modelrun.update()
          return jsonify({'message':'ModelRun submitted in queue','modelrun':modelrun_serializer(modelrun)}), 200
        else:
          error = {'message':"ModelRun {0} Doesn't have the necessary resources attached".format(modelrun),'missing':list(needed_resources-available_resources)}
          return jsonify(error), 400
      else:
        error = {'message':PROGRESS_STATES_MSG[modelrun.progress_state].format(modelrun_id=modelrun.id)}
        return jsonify(error), 400
    else:
      err = {"message":"ModelRun {0} Not Found".format(id)}
      return jsonify(err), 404




@blueprint.route("/<int:id>/progress")
@jwt_required()
@modelrun_authorization_required
def progress(id):
    modelrun = ModelRun.query.get(id)
    if modelrun:
      progress = {"modelrun_id":id,"state":modelrun.progress_state,"value":modelrun.progress_value}
      return jsonify(progress)
    else:
      err = {"error":"ModelRun {0} Not Found".format(id)}
      return jsonify(err), 404
