import sys
#sys.path.append("/opt/anaconda/bin")
sys.path.append("/var/www/vwadaptor")
sys.path.append("/opt/vw-py")

import os
import logging
import multiprocessing
import json
import pprint
import importlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from vwadaptor.settings import DevConfig, ProdConfig
from vwadaptor.modelrun.models import ModelRun, ModelResource, ModelProgress
from vwadaptor.user.models import User
from vwadaptor.constants import PROGRESS_STATES

from pyee import EventEmitter

import vwpy
from vwpy.modelschema import  load_schemas

def load_model_modules(modelschemas):
    model_modules={}
    for mschema in modelschemas:
        mod = importlib.import_module(modelschemas[mschema]['execution']['target']['module'])
        met = modelschemas[mschema]['execution']['target']['method']
        model_modules[modelschemas[mschema]['model']]={'module':mod,'method':getattr(mod, met)}
    return model_modules

def create_resource_mapping(schema,modelrun):
    resources = session.query(ModelResource).filter_by(modelrun_id=modelrun.id).all()
    mapping={}
    input_schema = schema['resources']['inputs']
    output_schema = schema['resources']['outputs']
    outfound = False
    outloc = '/tmp/modelrunoutputs'
    for r in resources:
        if not outfound:
            outloc = os.path.dirname(r.resource_location)
            outfound=True
        mapping[input_schema[r.resource_type]['mapsTo']]=r.resource_location
    for s in output_schema:
        mapping[output_schema[s]['mapsTo']]=os.path.join(outloc,output_schema[s]['name']+str(modelrun.id))
    return mapping


def resolve_output_map(mapping,schema):
    output_mapping={}
    for s in schema['resources']['outputs']:
        if schema['resources']['outputs'][s]['mapsTo'] in mapping:
            res_type=s
            loc = mapping[schema['resources']['outputs'][s]['mapsTo']]
            output_mapping[schema['resources']['outputs'][s]['mapsTo']]={'type':res_type,'location':loc}
    return output_mapping



def add_progress_event(dbsession,event):
  existing_event = session.query(
                    ModelProgress).filter_by(
                      modelrun_id=event.modelrun_id,
                      event_name=event.event_name
                    ).first()
  if existing_event:
    existing_event.progress_value = event.progress_value
  else:
    session.add(event)

  dbsession.commit()


ee = EventEmitter()
@ee.on('progress')
def on_progress(dbsession,modelrun_id,progress_state=PROGRESS_STATES['RUNNING'],**kwargs):
    #print 'updating progress'
    progress_event = ModelProgress()
    progress_event.event_name = kwargs['event_name']
    progress_event.event_description = kwargs['event_description']
    progress_event.progress_value = kwargs['progress_value']
    progress_event.modelrun_id = modelrun_id
    add_progress_event(dbsession,progress_event)
    dbsession.commit()


def run_model(dbsession,modelrun):
    mapping = create_resource_mapping(modelschemas[modelrun.model_name],modelrun)
    modelrun.progress_state = PROGRESS_STATES['RUNNING']
    dbsession.commit()
    kwargs = {'dbsession':dbsession,'modelrun_id':modelrun.id}
    kwargs.update(mapping)

    try:
        #run the model
        model_modules[modelrun.model_name]['method'](event_emitter=ee,**kwargs)
        output_mapping = resolve_output_map(mapping,modelschemas[modelrun.model_name])
        for m in output_mapping:
            output_resource = ModelResource()
            output_resource.resource_type=output_mapping[m]['type']
            output_resource.resource_location = output_mapping[m]['location']
            output_resource.resource_size = os.stat(output_resource.resource_location).st_size
            modelrun.resources.append(output_resource)
        modelrun.progress_state=PROGRESS_STATES['FINISHED']
        logging.info('done running::{modelrun}'.format(modelrun=modelrun))
    except:
        logging.info('Erorr Happended while running model:{modelrun}'.format(modelrun=modelrun))
        e = sys.exc_info()[0]
        print e
        modelrun.progress_state=PROGRESS_STATES['ERROR']
    dbsession.commit()


LOG_FILE = '/var/www/vwadaptor/model_runner.log'
logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG,format='%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S')


modelschemas = load_schemas()
model_modules = load_model_modules(modelschemas)


if os.environ.get("VWADAPTOR_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig

db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
# create a configured "Session" class
Session = sessionmaker(bind=db_engine)
# create a Session
session = Session()


modelruns = session.query(ModelRun).filter_by(progress_state=PROGRESS_STATES['QUEUED']).all()
if modelruns:
  logging.info('starting job on {0} queued modelruns'.format(len(modelruns)))
  for modelrun in modelruns:
    p = multiprocessing.Process(name='runmodel {0}'.format(modelrun.id), target=run_model,args=(session,modelrun,))
    p.start()
else:
  logging.info('No queued model run found on this turn.')
