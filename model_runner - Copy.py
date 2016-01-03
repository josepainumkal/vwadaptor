import sys
sys.path.append("/home/escenic/vwadaptor")
sys.path.append("/home/escenic/wcwave_adaptors")


import os
import logging
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from vwadaptor.settings import DevConfig, ProdConfig
from vwadaptor.modelrun.models import ModelRun, ModelResource, ModelProgress
from vwadaptor.user.models import User
from vwadaptor.constants import PROGRESS_STATES

import netCDF4 
from wcwave_adaptors.isnobal import isnobal 

from pyee import EventEmitter


LOG_FILENAME = '/home/escenic/vwadaptor/model_runner.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')


ee = EventEmitter()
if os.environ.get("VWADAPTOR_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig

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

@ee.on('progress')
def on_progress(dbsession,modelrun_id,progress_state=PROGRESS_STATES['RUNNING'],**kwargs):
  #print 'updating progress'
  progress_event = ModelProgress()
  progress_event.event_name = kwargs['event_name']
  progress_event.event_description = kwargs['event_description']
  progress_event.progress_value = kwargs['progress_value']
  progress_event.modelrun_id = modelrun_id
  add_progress_event(dbsession,progress_event)
  modelrun = session.query(ModelRun).filter_by(id=modelrun_id).first()
  modelrun.progress_state = progress_state
  modelrun.progress_value = kwargs['progress_value']
  dbsession.commit()


def run_model(dbsesion,modelrun):
  logging.debug('running modlerun:{modelrun}'.format(modelrun=modelrun))
  print 
  modelresource = session.query(ModelResource).filter_by(modelrun_id=modelrun.id,resource_type='input').first()
  input_path = modelresource.resource_location
  input_nc = netCDF4.Dataset(input_path) 
  output_path = input_path.split('.')[0]+'-output'+'.nc'
  kwargs = {'dbsession':session,'modelrun_id':modelrun.id}
  try:
    nc_out = isnobal(input_nc, output_path,event_emitter=ee,**kwargs)
    nc_out.close()
    output_resource = ModelResource()
    output_resource.resource_type='output'
    output_resource.resource_location = output_path
    output_resource.resource_size = os.stat(output_resource.resource_location).st_size
    modelrun.resources.append(output_resource)
    modelrun.progress_state=PROGRESS_STATES['FINISHED']
    logging.info('done running::{modelrun}'.format(modelrun=modelrun))
  except:
    logging.info('Erorr Happended while running model:{modelrun}'.format(modelrun=modelrun))
    modelrun.progress_state=PROGRESS_STATES['ERROR']
  dbsesion.commit()


db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
# create a configured "Session" class
Session = sessionmaker(bind=db_engine)
# create a Session
session = Session()  

# db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
# session_factory = sessionmaker(bind=db_engine)
# # create a Session
# Session = scoped_session(session_factory)
# session = Session()  




modelrun = session.query(ModelRun).filter_by(progress_state=PROGRESS_STATES['QUEUED'],model_name='isnobal').first()
#print modelruns
if modelrun:
  logging.info('starting job on queued modelrun: {modelrun}.'.format(modelrun=modelrun))
  run_model(session,modelrun)
else:
  logging.info('No queued model run found on this turn.')

  #t = threading.Thread(name='model_runner {0}'.format(modelrun.id), target=run_model,args=(session,modelrun,))
  #t.start()
#session.commit()


#session.add(modelrun)
#print 'after update:', modelrun.progress_state
#session.commit()

#session.close()
