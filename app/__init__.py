import os.path
import sys

from flask_api import FlaskAPI
from flask_restful import reqparse, Resource, Api
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy


import jwt

from app.config import bucketlist_config


db = SQLAlchemy()
auth = HTTPBasicAuth()


def create_app(config_name):
    from app.models import User, Bucketlist, BucketlistItems
    from app.resources import (RegisterUser, UserLogin, UserLogout,
                                 AddBucketlist, AddBucketlistItem, UpdateBucketlist)

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(bucketlist_config[config_name])
    scriptpath = os.path.dirname(__file__)
    filename = os.path.join(scriptpath, 'config.py')
    app.config.from_pyfile(filename)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['BUNDLE_ERRORS'] = True
    api = Api(app)
    db.init_app(app)

    # urls
    api.add_resource(
        RegisterUser, '/bucketlist_api/v1.0/auth/register', endpoint='register')
    api.add_resource(
        UserLogin, '/bucketlist_api/v1.0/auth/login', endpoint='login')
    api.add_resource(
        UserLogout, '/bucketlist_api/v1.0/auth/logout', endpoint='logout')
    api.add_resource(
        AddBucketlist, '/bucketlist_api/v1.0/bucketlists/', endpoint='bucketlists')
    api.add_resource(
        AddBucketlistItem, '/bucketlist_api/v1.0/bucketlists/<int:id>/items/', endpoint='items')
    api.add_resource(
        UpdateBucketlist, '/bucketlist_api/v1.0/bucketlists/<int:id>', endpoint='id')

    return app
