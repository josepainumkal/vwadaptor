import os
from functools import wraps

from flask import current_app as app
from flask_jwt import jwt_required, current_identity
from flask.ext.restless import ProcessingException

from .extensions import storage
from vwadaptor.modelrun.models import ModelRun, ModelResource

#
# @jwt_required()
# def authorize(**kwargs):
#     pass
#
def authorize_modelrun(id):
    modelrun = ModelRun.query.get(id)
    #print modelrun
    #raise ProcessingException(description='You are not authorized to access this ModelRun', code=401)
    if modelrun and modelrun.user_id != current_identity.id:
        raise ProcessingException(description='You are not authorized to access this ModelRun', code=401)

@jwt_required()
def modelresource_before_delete(instance_id=None, **kwargs):
    resource = ModelResource.query.get(instance_id)
    if not resource:
        return
    authorize_modelrun(resource.modelrun_id)
    obj = storage.get(resource.resource_name)
    if obj:
        if app.config['STORAGE_PROVIDER']=='LOCAL':
            path = storage.driver.get_object_cdn_url(obj._obj)
            os.unlink(path)
        else:
            obj.delete()


@jwt_required()
def modelrun_before_post(data=None, **kwargs):
    user_id = current_identity.id
    data['user_id'] = user_id
    return data


@jwt_required()
def modelrun_before_get(instance_id=None, **kwargs):
    authorize_modelrun(instance_id)


@jwt_required()
def modelrun_before_get_many(search_params=None, **kwargs):
    if search_params is None:
        return
    filt = dict(name='user_id', op='eq', val=current_identity.id)
    search_params['filters'] = [filt]



@jwt_required()
def modelrun_before_delete(instance_id=None, **kwargs):
    authorize_modelrun(instance_id)
    modelrun = ModelRun.query.get(instance_id)
    if modelrun:
        if modelrun.resources:
          for resource in modelrun.resources:
            modelresource_before_delete(instance_id=resource.id)
            resource.delete()
        if modelrun.progress_events:
          for event in modelrun.progress_events:
            event.delete()


def modelrun_authorization_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        id = kwargs['id']
        authorize_modelrun(id)
        return fn(*args, **kwargs)
    return decorator

@jwt_required()
def modelresource_before_get(instance_id, **kwargs):
    resource = ModelResource.query.get(instance_id)
    if not resource:
        return
    authorize_modelrun(resource.modelrun_id)

def modelresource_before_get_many(search_params=None, **kwargs):
    raise ProcessingException(description='You are not authorized to access this endpoint', code=401)

modelrun_preprocessors = {
    'GET_SINGLE':[
        modelrun_before_get
    ],
    'GET_MANY':[
        modelrun_before_get_many
    ],
    'POST': [
        modelrun_before_post
    ],
    'DELETE_SINGLE':[
        modelrun_before_delete
    ]
}


modelresource_preprocessors = {
    'GET_SINGLE':[
        modelresource_before_get
    ],
    'GET_MANY':[
        modelresource_before_get_many
    ],
    'DELETE_SINGLE':[
        modelresource_before_delete
    ]
}
