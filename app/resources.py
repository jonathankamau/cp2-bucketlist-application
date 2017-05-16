import os

from flask_api import FlaskAPI
from flask_restful import reqparse, Resource, Api
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from app.models import User, Bucketlist, BucketlistItems
from app.helpers import Helper

db = SQLAlchemy()
auth = HTTPBasicAuth()
helper = Helper()


class RegisterUser(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('firstname', type=str,
                                   required=True, help="First Name not given!")
        self.reqparse.add_argument('lastname', type=str,
                                   required=True, help="Last Name not given!")
        self.reqparse.add_argument('username', type=str,
                                   required=True, help="User Name not given!")
        self.reqparse.add_argument('password', type=str,
                                   required=True, help="Password not given!")

        super(RegisterUser, self).__init__()

    def get(self):
            response = ("Welcome to BucketList! To Register, "
                        "please make a POST /bucketlist_api/v1.0/auth/register with "
                        "your first and last name, username and password")

            return response

    def post(self):
        args = self.reqparse.parse_args()
        username = request.form.get('username')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        items = {"username": username, "firstname": firstname,
                 "lastname": lastname, "password": password}
        result = ['The following fields cannot be empty:']
        result_user = User.query.filter_by(username=username).first()
        db.session.remove()
        if result_user is not None:
            resp = "User already exists!"
        else:
            args = self.reqparse.parse_args()
            for key, value in items.items():
                if value == '':
                    result.append(key)
            if len(result) > 1:
                resp = ' '.join(result)
            else:
                user = User(firstname=args['firstname'], lastname=args['lastname'],
                            username=args['username'], password=args['password'])
                user.save()
                resp = "You have registered successfully"

        return resp

class UserLogin(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str,
                                   required=True, help="First Name not given!")
        self.reqparse.add_argument('password', type=str,
                                   required=True, help="Last Name not given!")

        self.generate_token = helper.generate_token

    def get(self):
        return ("Login required! Please make a POST /bucketlist_api/v1.0/auth/login with "
                "your username and password")

    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        result = ['The following fields cannot be empty:']
        user = {
            "username": username,
            "password": password
        }
        for key, value in user.items():
            if value == '':
                result.append(key)
        if len(result) > 1:
            resp = ' '.join(result)
        else:
            result_user = User.query.filter_by(username=username).first()
            #db.session.remove()
            if result_user.check_password(password):
                token = result_user.generate_token()
                token_response = {'token': token}, 200
                resp = "You have logged in successfully {}".format(token_response)
            else:
                resp = "Could not log you in! Check your username and password and try again!"

        return resp

class UserLogout(Resource):
    def __init__(self):
        pass

    def get(self):
        token = request.headers.get('Authorization')
        db.session.delete(token)
        return "You have logged out successfully"

class AddBucketlist(Resource):
    decorators = [auth.login_required]
    def __init__(self):
        self.token = request.headers.get('Authorization')

    def post(self):
        name = str(request.data.get('name', ''))
        if name:
            bucketlist = Bucketlist(name=name, created_by=user.user_id)
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

    def get(self):
        bucketlists = Bucketlist.get_all()
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


class AddBucketlistItem(Resource):
    decorators = [auth.login_required]
    def __init__(self, userid):
        self.bucketlist = Bucketlist.query.filter_by(user_id=userid).first()
        if not self.bucketlist:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

    def post(self):
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

class UpdateBucketlist(Resource):
    decorators = [auth.login_required]
    def __init__(self, userid):
        self.bucketlist = Bucketlist.query.filter_by(user_id=userid).first()
        super(UpdateBucketlist, self).__init__()

    def delete(self):
        if not self.bucketlist:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        self.bucketlist.delete()
        return {
            "message": "bucketlist {} deleted successfully".format(self.bucketlist.bucketlist_id)
        }, 200

    def put(self):
        name = str(request.data.get('name', ''))
        self.bucketlist.name = name
        self.bucketlist.save()
        response = jsonify({
            'id': self.bucketlist.bucketlist_id,
            'name': self.bucketlist.name,
            'date_created': self.bucketlist.date_created,
            'date_modified': self.bucketlist.date_modified
        })
        response.status_code = 200
        return response

    def get(self):
        response = jsonify({
            'id': self.bucketlist.bucketlist_id,
            'name': self.bucketlist.name,
            'date_created': self.bucketlist.date_created,
            'date_modified': self.bucketlist.date_modified
        })
        response.status_code = 200
        return response

    