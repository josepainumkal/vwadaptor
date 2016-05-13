from pyee import EventEmitter
from vwadaptor.modelrun.models import ModelRun, ModelResource, ModelProgress
from vwadaptor.constants import PROGRESS_STATES

ee = EventEmitter()

@ee.on('progress')
def on_progress(db,modelrun_id,progress_state=PROGRESS_STATES['RUNNING'],**kwargs):
    #print 'updating progress'
    progress_event = ModelProgress()
    progress_event.event_name = kwargs['event_name']
    if 'event_description' in kwargs:
        progress_event.event_description = kwargs['event_description']
    if 'progress_value' in kwargs:
        progress_event.progress_value = kwargs['progress_value']
    progress_event.modelrun_id = modelrun_id
    add_progress_event(db,progress_event)
    db.commit()

def add_progress_event(db,event):
  existing_event = db.query(
                    ModelProgress).filter_by(
                      modelrun_id=event.modelrun_id,
                      event_name=event.event_name
                    ).first()
  if existing_event:
    existing_event.progress_value = event.progress_value
    existing_event.event_description = event.event_description
  else:
    db.add(event)

  db.commit()
