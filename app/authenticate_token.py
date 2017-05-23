import os


from flask import g
from flask_httpauth import HTTPTokenAuth

from app.models import User



auth_token = HTTPTokenAuth('Bearer')

@auth_token.verify_token
def verify_token(token):
    g.current_user = User.verify_auth_token(token)
    return g.current_user not in ['Invalid Token!', 'Expired Token!']

@auth_token.error_handler
def unauthorized_token():
    return {'Error':'Please send a valid authentication token'}, 401
