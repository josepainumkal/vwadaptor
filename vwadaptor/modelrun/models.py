import datetime as dt
import os

from vwadaptor.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK
)

from flask import url_for

from vwadaptor.constants import PROGRESS_STATES
from sqlalchemy.ext.hybrid import hybrid_property


class ModelRun(SurrogatePK, Model):

    __tablename__ = 'modelruns'

    title = Column(db.String(80), unique=False, nullable=False)
    model_name = Column(db.String(30), nullable=False)
    resources = relationship(
        'ModelResource', backref='modelrun', lazy='dynamic')
    user_id = Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #'not_started','queued', 'running','finished','error'
    progress_state = Column(db.Enum(*tuple(PROGRESS_STATES.values()),
                                    name='progress_states'),
                            default=PROGRESS_STATES['NOT_STARTED'])
    progress_value = Column(db.Float(10), nullable=True, default=0.0)
    progress_events = relationship(
        'ModelProgress', backref='modelrun', lazy='dynamic')
    created_at = Column(db.DateTime, nullable=False,
                        default=dt.datetime.utcnow)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<ModelRun({id}:{name})>'.format(id=self.id, name=self.title)


class ModelResource(SurrogatePK, Model):
    __tablename__ = 'modelresources'
    resource_type = Column(db.String(80), nullable=False)
    resource_url = Column(db.String(200), nullable=False)
    resource_name = Column(db.String(200), nullable=False)
    resource_size = Column(db.Integer)
    modelrun_id = Column(db.Integer, db.ForeignKey('modelruns.id'))
    created_at = Column(db.DateTime, nullable=True, default=dt.datetime.utcnow)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<ModelResource({type}--{name})>'.format(type=self.resource_type,name=self.resource_name)



class ModelProgress(SurrogatePK, Model):
    __tablename__ = 'modelprogress'
    event_name = Column(db.String(80), nullable=False)
    event_description = Column(db.String(500), nullable=False)
    progress_value = Column(db.Float(), default=0)
    modelrun_id = Column(db.Integer, db.ForeignKey('modelruns.id'))
    created_at = Column(db.DateTime, nullable=True, default=dt.datetime.utcnow)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<ModelProgress({event_name}--{name})>'.format(event_name=self.event_name,event_description=self.event_description)
