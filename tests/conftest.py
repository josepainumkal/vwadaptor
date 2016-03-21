# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import os
import shutil
import pytest
from webtest import TestApp

from vwadaptor.settings import TestConfig as config
from vwadaptor.app import create_app
from vwadaptor.database import db as _db

from .factories import UserFactory

from vwadaptor.modelrun.models import ModelRun

TEST_DIR = os.path.abspath(os.path.dirname(__file__))

@pytest.yield_fixture(scope='function')
def app():
    os.makedirs(config.STORAGE_CONTAINER)
    _app = create_app(config)
    with _app.app_context():
        _db.create_all()
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    _db.drop_all()
    shutil.rmtree(config.STORAGE_CONTAINER)
    ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture
def user(db):
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user

@pytest.fixture
def modelrun(db):
    m = ModelRun(title="test modelrun isnobal 1",model_name="isnobal",user_id=1)
    m=m.save()
    return m
