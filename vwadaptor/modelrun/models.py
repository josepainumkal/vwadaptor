import datetime as dt

from vwadaptor.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK
)

from vwadaptor.constants import PROGRESS_STATES
#from marshmallow import Schema, fields, pprint
from sqlalchemy.ext.hybrid import hybrid_property

class ModelRun(SurrogatePK, Model):

    __tablename__ = 'modelruns'
    #uuid = Column(db.String(80), unique=True, nullable=False)
    title = Column(db.String(80), unique=True, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    model_name = Column(db.String(30), nullable=False)
    resources = relationship('ModelResource', backref='modelrun', lazy='dynamic')
    #progress = relationship('ModelProgress', uselist=False,backref='progress')
    user_id = Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    #'not_started','queued', 'running','finished','error'
    progress_state = Column('state', db.Enum(*tuple(PROGRESS_STATES.values())), default=PROGRESS_STATES['NOT_STARTED'])
    progress_value = Column(db.Float(10), nullable=True, unique=True,default=0.0)

    # @hybrid_property
    # def progress(self):
    #     return {"modelrun_id":self.id,"state":self.progress_state,"value":self.progress_value}

    def __init__(self,**kwargs):
        db.Model.__init__(self, **kwargs)
    def __repr__(self):
        return '<ModelRun({name})>'.format(name=self.title)


class ModelResource(SurrogatePK, Model):
    __tablename__ = 'modelresources'
    resource_type = Column(db.String(80), nullable=False)
    #resource_url = Column(db.String(200), nullable=True)
    resource_location = Column(db.String(80), nullable=True, unique=True)
    resource_size = Column(db.Integer)
    modelrun_id = Column(db.Integer, db.ForeignKey('modelruns.id'))

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<ModelResource({type}--{name})>'.format(type=self.file_type,name=self.file_location)

# class ModelRunSchema(Schema):
#     id = fields.Integer()
#     title = fields.String()
#     model_name = fields.String()

#     def make_object(self, data):
#         print('MAKING OBJECT FROM', data)
#         return ModelRun(**data)

# modlerun_schema = ModelRunSchema()
# def modelrun_serializer(instance):
#     return modlerun_schema.dump(instance).data



# class ModelProgress(SurrogatePK, Model):
#     __tablename__ = 'modelprogress'
    
#     state = Column('state', db.Enum('queued', 'running','finished','error'), default='queued')
#     value = Column(db.Float(10), nullable=False, unique=True)
#     model_run_id = Column(db.Integer, db.ForeignKey('modelruns.id'))

#     def __init__(self, **kwargs):
#         db.Model.__init__(self, **kwargs)

#     def __repr__(self):
#         return '<ModelResource({type}--{name})>'.format(type=self.file_type,name=self.file_location)



# standard decorator style
# @event.listens_for(ModelRun, 'after_insert')
# def receive_after_insert(mapper, connection, modelrun):
#     print connection
#     progVals = {'value':0,'model_run_id':modelrun.id}
#     progress = ModelProgress(**progVals)
#     connection.add(progress)
#     connection.commit()