# JWT Token auth
from vwadaptor.userdatastore import user_datastore
from flask.ext.security.utils import encrypt_password, verify_password
from flask_jwt import JWT
def authenticate(username, password):
    user = user_datastore.find_user(email=username)
    if user and user.confirmed_at and username == user.email and verify_password(password, user.password):
        return user
    return None


def load_user(payload):
    user = user_datastore.find_user(id=payload['identity'])
    if user.confirmed_at:
        return user
    return None

jwt = JWT(app=None,authentication_handler=authenticate, identity_handler=load_user)
