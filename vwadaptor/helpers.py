import os
import random, string
from sqlalchemy.inspection import inspect
from flask_restless.helpers import to_dict
import json
from vwadaptor.modelrun.models import ModelRun, ModelResource
from vwadaptor.serializers import UserSchema, ModelResourceSchema, ModelRunSchema
from .extensions import storage
def get_relationships(model):
  '''
    returns the sqlalchemy relationships of a model class
  '''
  rels = inspect(model).relationships
  return [str(rel).split('.')[-1] for rel in rels]


def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def generate_file_name(filepath):
  '''
    generates a filename that does not exist in filepath
  '''


  dirname = os.path.dirname(filepath)
  orig_file_name = os.path.basename(filepath)
  filename = os.path.basename(filepath)
  #filename =filename.rsplit('.',1)[0] + str(i)+'.' + filename.rsplit('.',1)[-1]
  while(os.path.isfile(os.path.join(dirname,filename))):
    filename =orig_file_name.rsplit('.',1)[0] + randomword(5)+'.'+ orig_file_name.rsplit('.',1)[-1]
  return filename

def get_relationships_map(model):
  relationships = get_relationships(model)
  rels = {}
  for rel in relationships:
    rels[rel]=[]
  return rels


user_schema = UserSchema()
modelresource_schema = ModelResourceSchema()
modelrun_schema = ModelRunSchema()

def user_serializer(instance):
    return user_schema.dump(instance).data

def modelresource_serializer(instance):
    return modelresource_schema.dump(instance).data

def modelrun_serializer(instance):
    return modelrun_schema.dump(instance).data

def modelrun_deserializer(data):
    return modelrun_schema.load(data).data


def modelresource_deserializer(data):
    return modelresource_schema.load(data).data



def model_run_after_get_many(result=None, search_params=None, **kw):
  result['objects'] = [modelrun_deserializer(obj) for obj in result['objects']]

def modelprogress_after_get_many(result=None, search_params=None, **kw):
  #result [dictio for dictio in search_params['filters'] if dictio['name'] =='modelrun_id']
  pass

def model_run_before_delete(instance_id,**kw):
  modelrun = ModelRun.query.get(instance_id)
  if modelrun:
    if modelrun.resources:
      for resource in modelrun.resources:
        model_resource_before_delete(resource.id)
        resource.delete()
    if modelrun.progress_events:
      for event in modelrun.progress_events:
        event.delete()

#def model_run_before_delete_many(search_params=None,**kw):
#  print search_params
  # modelruns = ModelRun.query.filter_by(search_params).all()
  # if modelruns:
  #   for modelrun in modelruns:
  #     if modelrun.resources:
  #       for resource in modelrun.resources:
  #         model_resource_before_delete(resource.id)
  #         resource.delete()
  #     if modelrun.progress_events:
  #       for event in modelrun.progress_events:
  #         event.delete()


def model_resource_before_delete(instance_id,**kw):
  resource = ModelResource.query.get(instance_id)
  if resource:
      obj = storage.get(resource.resource_name)
      if obj:
          obj.delete()
