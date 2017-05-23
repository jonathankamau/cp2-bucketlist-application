import os

import json
from flask_api import FlaskAPI
from flask_restful import reqparse, Resource, Api, marshal, fields
from flask_httpauth import HTTPTokenAuth
from flask import g, request, jsonify, abort, Blueprint, url_for
from flask_sqlalchemy import SQLAlchemy
from app.authenticate_token import auth_token


from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from app.models import User, Bucketlist, BucketlistItems
from app.schemas import reg_schema, user_login, bucketlist_schema, flask_bucketlist

db = SQLAlchemy()


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
            result, errors = reg_schema.load(items)
            if errors:

                resp = {'errors': errors}
            else:
                user = User(username=username, firstname=firstname,
                            lastname=lastname, password=password)
                user.save()
                resp = {'response': 'You have registered successfully',
                        'result': result}

        return resp


class UserLogin(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str,
                                   required=True, help="First Name not given!")
        self.reqparse.add_argument('password', type=str,
                                   required=True, help="Last Name not given!")

    # def verify_token(self, token):
    #     serial = Serializer(os.getenv('SECRET'))
    #     try:
    #         data = serial.loads(token)
    #     except SignatureExpired:
    #         return "Expired Token!"  # valid token, but expired
    #     except BadSignature:
    #         return "Invalid Token"  # invalid token
    #     user = User.query.get(data['user_id'])
    #     return user

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
            # db.session.remove()
            if result_user.check_password(password):
                token = result_user.generate_token()
                resp = {'token': token,
                        'message': "You have logged in successfully"}, 200

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


class BucketlistAPI(Resource):
    decorators = [auth_token.login_required]

    def __init__(self):
        #self.token = request.headers.get('Authorization')
        self.page = request.args.get('page', 1, type=int)
        self.max_limit = 100
        self.request_limit = request.args.get('limit', 2, type=int)
        self.limit = min(self.request_limit, self.max_limit)
        self.search_term = request.args.get('q', None, type=str)
        self.query_items = ''
        self.query = ''
        self.item_format = {
            'id': fields.Integer,
            'name': fields.String,
            'items': fields.String,
            'date_created': fields.DateTime,
            'date_modified': fields.DateTime
        }

    def post(self):
        name = str(request.data.get('name', ''))
        if name:
            bucketlist = Bucketlist(
                name=name, created_by=g.current_user.username, user_id=g.current_user.user_id)
            bucketlist.save()
            item_object = 'No items yet!'

            response = jsonify({
                'id': bucketlist.bucketlist_id,
                'name': bucketlist.name,
                'created_by': g.current_user.username,
                'items': item_object,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified
            })
            response.status_code = 201
            return response

    def get(self):
        if not self.search_term:
            bucketlists_by_page = Bucketlist.query.filter_by(
                user_id=g.current_user.user_id).order_by(
                    Bucketlist.date_modified.desc()).paginate(
                    self.page, self.limit, error_out=True)

        else:
            bucketlists_by_page = Bucketlist.query.filter_by(
                user_id=g.current_user.user_id).filter(Bucketlist.name.ilike(
                    '%' + self.search_term + '%')).order_by(
                        Bucketlist.date_modified.desc()).paginate(
                            self.page, self.limit, error_out=True)

        if not bucketlists_by_page.items and self.search_term:
            error_response = {'error': 'Not found',
                              'message': 'No results'}, 404
            return error_response
        if not bucketlists_by_page.items:
            error_response = {'error': 'Not found',
                              'message': 'No bucketlists have been added'}, 404
            return error_response

        if bucketlists_by_page.has_next:
            url_next = url_for(request.endpoint, page=self.page + 1,
                               limit=self.limit, query=self.search_term)
            # "?page=" + str(self.page + 1) +
            # "&limit=" + str(self.limit) +
            # self.query.format(self.query_items))
        else:
            url_next = "Null"

        if bucketlists_by_page.has_prev:
            url_prev = (url_for(request.endpoint) +

                        "?page=" + str(self.page - 1) +
                        "&limit=" + str(self.limit) +
                        self.query.format(self.query_items))

        else:

            url_prev = "Null"
        result = flask_bucketlist.dump(list(bucketlists_by_page.items))
        return {"info": {"next_page": url_next,
                         "previous_page": url_prev,

                         "total_pages": bucketlists_by_page.pages},

                "bucketlists": result.data
                # marshal(bucketlists_by_page.items, self.item_format)

                }, 200

        # print(bucketlists_by_page.items)
        # response = bucketlists_by_page
        # response.status_code = 200
        # return response

        #bucketlists = Bucketlist.get_all()
        # results = []

        # for bucketlist in bucketlists:
        #     bucketlist_items = BucketlistItems(
        #         bucketlist_id=bucketlist.bucketlist_id)
        #     if bucketlist_items is None:
        #         item_object = 'No items yet!'
        #     else:
        #         item_object = {
        #             'id': bucketlist_items.item_id,
        #             'name': bucketlist_items.name,
        #             'date_created': bucketlist_items.date_created,
        #             'date_modified': bucketlist_items.date_modified,
        #             'done': bucketlist_items.done
        #         }
        #     obj = {
        #         'id': bucketlist.bucketlist_id,
        #         'name': bucketlist.name,
        #         'items': item_object,
        #         'date_created': bucketlist.date_created,
        #         'date_modified': bucketlist.date_modified
        #     }
        #     results.append(obj)
        # response = jsonify(results)
        # response.status_code = 200
        # return response


class BucketlistItem(Resource):
    decorators = [auth_token.login_required]

    # def __init__(self, bucketlist_id, item_id):
    #     self.bucketlist_id = bucketlist_id
    #     self.item_id = item_id

    def post(self, bucketlist_id):
        name = request.form.get('name')
        description = request.form.get('description')
        self.bucketlist = Bucketlist.query.filter_by(
            bucketlist_id=bucketlist_id, created_by=g.current_user.username).first()
        if not self.bucketlist:
            # Raise an HTTPException with a 404 not found status code
            response = jsonify({'message': 'Bucketlist does not exist!'})
            response.status_code = 404
        else:
            name = str(request.data.get('name', ''))
            if name:
                bucketlist_items = BucketlistItems(
                    name=name, bucketlist_id=bucketlist_id, description=description, user_id=g.current_user.user_id, created_by=g.current_user.username)
                bucketlist_items.save()
                bucketlist_created_item = BucketlistItems.query.filter_by(
                    name=name, created_by=g.current_user.username).first()
                response = jsonify({
                    'message': 'Bucketlist Item Created Successfully',
                    'id': bucketlist_created_item.item_id,
                    'name': bucketlist_created_item.name,
                    'description': bucketlist_created_item.description,
                    'date_created': bucketlist_created_item.date_created,
                    'date_modified': bucketlist_created_item.date_modified,
                    'done': bucketlist_created_item.done,
                    'created_by': bucketlist_created_item.created_by
                })
                response.status_code = 201

        return response

    def put(self, bucketlist_id, item_id):
        #item_id = str(request.data.get('item_id', ''))
        name = request.form.get('name')
        description = request.form.get('description')
        done = request.form.get('done')
        if item_id:
            edit_item = BucketlistItems.query.filter_by(
                item_id=item_id, bucketlist_id=bucketlist_id, created_by=g.current_user.username).first()
            if name == '':
                name = edit_item.name
            if description == '':
                description = edit_item.description
            if done == '':
                done = edit_item.done

            edit_item.name = name
            edit_item.description = description
            edit_item.done = done

            edit_item.save()
         
            response = jsonify({
                'message': 'Bucketlist Item Updated Successfully',
                'id': edit_item.item_id,
                'name': edit_item.name,
                'description': edit_item.description,
                'date_created': edit_item.date_created,
                'date_modified': edit_item.date_modified,
                'done': edit_item.done,
                'created_by': edit_item.created_by
            })
            response.status_code = 201

            return response

    def delete(self, bucketlist_id, item_id):
        print(bucketlist_id, item_id)
        self.item_id = request.form.get('item_id')
        delete_item = BucketlistItems.query.filter_by(
            item_id=self.item_id, created_by=g.current_user.username).first()
        if not delete_item:
            response = jsonify({'message': 'Bucketlist item does not exist!'})
            response.status_code = 404
        else:
            name = delete_item.name
            delete_item.delete()
            return {
                "message": "bucketlist item {} deleted successfully".format(name)
            }, 200


class UpdateBucketlist(Resource):
    decorators = [auth_token.login_required]

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
