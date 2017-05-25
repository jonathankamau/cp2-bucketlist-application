import os.path
import sys

from flask_api import FlaskAPI
from flask_restful import reqparse, Resource, Api
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import request, jsonify, abort, Blueprint
from flask_sqlalchemy import SQLAlchemy


from app.config import bucketlist_config


db = SQLAlchemy()
auth = HTTPBasicAuth()


def create_app(config_name):
    from app.models import User, Bucketlist, BucketlistItems
    from app.resources import (RegisterUser, UserLogin,
                               BucketlistAPI, BucketlistItem,
                               GetBucketlistItem, GetBucketlist, UpdateBucketlist)

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(bucketlist_config[config_name])
    scriptpath = os.path.dirname(__file__)
    filename = os.path.join(scriptpath, 'config.py')
    app.config.from_pyfile(filename)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BUNDLE_ERRORS'] = True

    api_blueprint = Blueprint('api', __name__)
    api = Api(api_blueprint)


    db.init_app(app)

    # urls
    api.add_resource(
        RegisterUser, '/auth/register', endpoint='register')
    api.add_resource(
        UserLogin, '/auth/login', endpoint='login')
    api.add_resource(
        BucketlistAPI, '/bucketlists/', endpoint='bucketlists')
    api.add_resource(
        GetBucketlist, '/bucketlists/<int:bucketlist_id>', endpoint='bucketlist-search')
    api.add_resource(
        BucketlistItem, '/bucketlists/<int:bucketlist_id>/items/', endpoint='items')
    api.add_resource(
        BucketlistItem, '/bucketlists/<int:bucketlist_id>/items/<int:item_id>',
        endpoint='edit-items')
    api.add_resource(
        UpdateBucketlist, '/bucketlists/<int:bucketlist_id>', endpoint='update')
    api.add_resource(
        GetBucketlistItem, '/bucketlists/<int:bucketlist_id>/items/<int:item_id>/',
        endpoint='item-search')

    app.register_blueprint(api_blueprint, url_prefix='/bucketlist_api/v1.0')

    return app
