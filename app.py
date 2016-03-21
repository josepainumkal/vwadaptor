import os
import time

from vwadaptor.settings import DevConfig, ProdConfig
from vwadaptor.app import create_app
from vwadaptor.extensions import db


if os.environ.get("VWADAPTOR_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig


'''This is a temporary fix for allowing docker-compose to work.
As docker-copose doesn't have any mechanism yet for health check of dependent services
This is the only way to wait for postgres and any other container(swift perhaps) to start
'''
time.sleep(10)
app = create_app(config)


@app.before_first_request
def create_db():
    #db.drop_all()
    db.create_all()

from flask_jwt import jwt_required,current_identity

@app.route('/testjwt',methods=['GET'])
@jwt_required()
def test():
    return "You are: %s" % current_identity.email
