import os

from flask_api import FlaskAPI
from flask import request, jsonify, abort
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

import jwt

from instance.config import bucketlist_config

bcrypt = Bcrypt()
db = SQLAlchemy()


def create_app(config_name):
    from app.models import User, Session, Bucketlist, BucketlistItems

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(bucketlist_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    db.init_app(app)

    @app.route('/bucketlist_api/v1.0/auth/register', methods=['GET', 'POST'])
    def register_user():
        if request.method == 'GET':
            response = ("Welcome to BucketList! To Register, "
                        "please make a POST /bucketlist_api/v1.0/auth/register with "
                        "your first and last name, username and password")

            return response
        else:
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            username = request.form.get('username')
            password = request.form.get('password')
            if username and password:
                user = User(firstname=firstname, lastname=lastname,
                            username=username, password=password)
                user.save()
                return "You have registered successfully"
            else:
                return "Could not save user information!"
    @app.route('/bucketlist_api/v1.0/auth/login', methods=['GET', 'POST'])
    def user_login():
        if request.method == 'GET':
            return ("Login required! Please make a POST /bucketlist_api/v1.0/auth/login with "
                    "your username and password")

        else:
            username = request.form.get('username')
            password = request.form.get('password')

            user = {
                "username": username,
                "password": password
                }
            result_user = User.query.filter_by(username=username).first()
            db.session.remove()
            if result_user.check_password(password) is True:
                secret_key = os.getenv('SECRET')
                jwt_string = jwt.encode(user, secret_key)
                session = Session(user_id=result_user.user_id, token=jwt_string)
                session.save()
                return "You have logged in successfully"
            else:
                return "Could not log you in! Check your username and password and try again!"

    @app.route('/bucketlist_api/v1.0/auth/logout', methods=['GET'])
    def user_logout():
        token = request.headers.get('Authorization')
        session = Session.query.filter_by(token=token)
        Session.query.filter(Session.user_id == session.user_id).delete()
        db.session.remove()
        return "You have logged out successfully"

    @app.route('/bucketlist_api/v1.0/bucketlists/', methods=['POST', 'GET'])
    def bucketlists():
        token = request.headers.get('Authorization')
        session = Session.query.filter_by(token=token).first()
        db.session.remove()
        if request.method == "POST":
            name = str(request.data.get('name', ''))
            if name:
                bucketlist = Bucketlist(name=name, created_by=session.user_id)
                bucketlist.save()
                item_object = 'No items yet!'

                response = jsonify({
                    'id': bucketlist.bucketlist_id,
                    'name': bucketlist.name,
                    'items': item_object,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                })
                response.status_code = 201
                return response
        else:
            # GET
            bucketlists = Bucketlist.get_all(session.user_id)
            results = []

            for bucketlist in bucketlists:
                bucketlist_items = BucketlistItems(
                    bucketlist_id=bucketlist.bucketlist_id)
                if bucketlist_items is None:
                    item_object = 'No items yet!'
                else:
                    item_object = {
                        'id': bucketlist_items.item_id,
                        'name': bucketlist_items.name,
                        'date_created': bucketlist_items.date_created,
                        'date_modified': bucketlist_items.date_modified,
                        'done': bucketlist_items.done
                    }
                obj = {
                    'id': bucketlist.bucketlist_id,
                    'name': bucketlist.name,
                    'items': item_object,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/bucketlist_api/v1.0/bucketlists/<int:id>/items/', methods=['POST', 'GET'])
    def item_bucketlist(id, **kwargs):
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if not bucketlist:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == "POST":
            name = str(request.data.get('name', ''))
            if name:
                bucketlist_items = BucketlistItems(name=name)
                bucketlist_items.save()
                response = jsonify({
                    'id': bucketlist_items.id,
                    'name': bucketlist_items.name,
                    'date_created': bucketlist_items.date_created,
                    'date_modified': bucketlist_items.date_modified
                })
                response.status_code = 201
                return response

    @app.route('/bucketlist_api/v1.0/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def bucketlist_manipulation(id, **kwargs):
     # retrieve a buckelist using it's ID
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if not bucketlist:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == 'DELETE':
            bucketlist.delete()
            return {
                "message": "bucketlist {} deleted successfully".format(bucketlist.id)
            }, 200

        elif request.method == 'PUT':
            name = str(request.data.get('name', ''))
            bucketlist.name = name
            bucketlist.save()
            response = jsonify({
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified
            })
            response.status_code = 200
            return response

    return app
