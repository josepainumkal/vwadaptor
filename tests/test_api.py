# -*- coding: utf-8 -*-
import os
import pytest
import json

from flask import url_for


from vwadaptor.user.models import User
from vwadaptor.helpers import modelrun_serializer
from .factories import UserFactory
from .conftest import TEST_DIR

from vwpy.modelschema import load_schemas

schemas = load_schemas()
class TestModelRun:
    def test_create_modelrun(self,testapp):
        modelrun=dict(title="test modelrun isnobal 1",model_name="isnobal",user_id=1)
        res = testapp.post_json('/api/modelruns', modelrun)
        assert res.status_code == 201
        assert bool(res.json['id'])
        assert len(res.json['resources'])==0

    def test_get_modelrun(self,testapp,modelrun):
        res = testapp.get('/api/modelruns/{id}'.format(id=modelrun.id))
        assert res.status_code == 200
        assert res.json['id']==modelrun.id

    def test_delete_modelrun(self,testapp,modelrun):
        res = testapp.delete('/api/modelruns/{id}'.format(id=modelrun.id))
        assert res.status_code == 204

    def test_delete_modelrun(self,testapp,modelrun):
        res = testapp.delete('/api/modelruns/{id}'.format(id=modelrun.id))
        assert res.status_code == 204

    def test_put_modelrun(self,testapp,modelrun):
        new_title="Changed Title"
        res = testapp.put_json('/api/modelruns/{id}'.format(id=modelrun.id),{'title':new_title})
        assert res.status_code == 200
        assert res.json['title'] == new_title

    def test_upload_resource(self,testapp,modelrun):
        resource_name = 'isnobal.nc'
        files = [('file',os.path.join(TEST_DIR,'data/'+resource_name))]
        res = testapp.post('/api/modelruns/{id}/upload'.format(id=modelrun.id),params=[('resource_type','input')],upload_files=files)
        assert res.status_code == 201
        assert res.json['resource']['resource_name'] == resource_name
        assert resource_name in res.json['resource']['resource_url']

    def test_start_modelrun_fail(self,testapp,modelrun):
        res = testapp.put('/api/modelruns/{id}/start'.format(id=modelrun.id),expect_errors=True)
        assert res.status_code == 400
        assert set(res.json['missing']) <= set(schemas[modelrun.model_name]['resources']['inputs'].keys())

    def test_start_modelrun_pass(self,testapp,modelrun):
        resource_name = 'isnobal.nc'
        files = [('file',os.path.join(TEST_DIR,'data/'+resource_name))]
        res = testapp.post('/api/modelruns/{id}/upload'.format(id=modelrun.id),params=[('resource_type','input')],upload_files=files)
        assert res.status_code == 201
        res = testapp.put('/api/modelruns/{id}/start'.format(id=modelrun.id))
        assert res.status_code == 200
