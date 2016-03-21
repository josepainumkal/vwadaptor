import os
import time
import requests
import shutil
from vwpy.modelschema import load_schemas
from modelrunner import ModelRunner

from config import db, celery, storage

from vwadaptor.modelrun.models import ModelRun, ModelResource, ModelProgress
from vwadaptor.user.models import User
from vwadaptor.helpers import modelrun_serializer
from vwadaptor.constants import PROGRESS_STATES
from util import rand_str
from event_handler import ee

schemas = load_schemas()

model_runners = {}
for model_name in schemas:
    model_runners[model_name] = ModelRunner(schemas,model_name)

@celery.task(name='vwadaptor.run')
def run_model(modelrun_id):
    modelrun = db.query(ModelRun).get(modelrun_id)
    try:
        tmp_dir = os.path.join('/tmp/modelruns/',str(modelrun.id))
        os.makedirs(tmp_dir)

        modelrun.progress_state = PROGRESS_STATES['RUNNING']
        db.commit()

        kwargs = {'db':db,'modelrun_id':modelrun.id}

        modelrunner = model_runners[modelrun.model_name]

        input_resource_map = modelrunner.get_resource_map()
        input_map = resolve_input_map(tmp_dir,input_resource_map,modelrun.resources)
        output_resource_map = modelrunner.get_resource_map(type='outputs')
        output_map = resolve_output_map(tmp_dir,output_resource_map)

        kwargs.update(input_map)
        kwargs.update(output_map)
        module, method = modelrunner.get_model_runner()
        method(event_emitter=ee,**kwargs)

        # save the output resources now
        resources = create_output_resources(modelrunner,output_map)

        modelrun.resources.extend(resources)
        modelrun.progress_state=PROGRESS_STATES['FINISHED']
    except:
        modelrun.progress_state=PROGRESS_STATES['ERROR']
    db.commit()

    # clean up
    shutil.rmtree(tmp_dir)

def create_output_resources(modelrunner,output_map):
    resources = []
    for m in output_map:
        if os.path.exists(output_map[m]):
            obj = storage.container.upload_object(output_map[m],os.path.basename(output_map[m]))
            output_resource = ModelResource()
            output_resource.resource_type = modelrunner.get_resource_type_from_map(m,'outputs')
            output_resource.resource_name = obj.name
            output_resource.resource_size = obj.size
            resources.append(output_resource)
    return resources
def resolve_input_map(tmp_dir,resource_map,resources):
    m = {}
    for r in resources:
        obj = storage.get(r.resource_name)
        tmp_path = os.path.join(tmp_dir,r.resource_name)
        storage.driver.download_object(obj=obj._obj,overwrite_existing=True,
                                       destination_path=tmp_path)
        m[resource_map[r.resource_type]['mapsTo']]= tmp_path
    return m

def resolve_output_map(tmp_dir,resource_map):
    m={}
    print rand_str()
    for r in resource_map:
        m[resource_map[r]['mapsTo']] = os.path.join(tmp_dir,resource_map[r]['name']+rand_str()+'.'+resource_map[r]['type'])
    return m
