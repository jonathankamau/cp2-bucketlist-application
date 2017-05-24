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
from app.schemas import reg_schema, user_login, bucketlist_schema

# initialize the database
db = SQLAlchemy()


class RegisterUser(Resource):
    """ resource class to register the user """

    def __init__(self):
        # initialize the class
        # initialize regparse for validation
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
        """ if user attempts to use get, he is instructed to use post """
        response = ("Welcome to BucketList! To Register, "
                    "please make a POST /bucketlist_api/v1.0/auth/register with "
                    "your first and last name, username and password")

        return response

    def post(self):
        """ allows the user to register using post """
        # gets the input details of the user
        username = request.form.get('username')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        items = {"username": username, "firstname": firstname,
                 "lastname": lastname, "password": password}
        result = ['The following fields cannot be empty:']
        # checks if the user already exisys
        result_user = User.query.filter_by(username=username).first()
        db.session.remove()
        if result_user is not None:
            resp = "User already exists!"
        else:
           # appends the result to its corresponding schema
            result, errors = reg_schema.load(items)
            # captures errors if any
            if errors:

                resp = {'errors': errors}
            else:
                # saves the user details to the database
                user = User(username=username, firstname=firstname,
                            lastname=lastname, password=password)
                user.save()
                # gives the return
                resp = {'response': 'You have registered successfully',
                        'result': result}

        return resp


class UserLogin(Resource):
    """ class resource that allows the user to login """

    def __init__(self):
        # initialize the class
        # initialize regparse for validation
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str,
                                   required=True, help="First Name not given!")
        self.reqparse.add_argument('password', type=str,
                                   required=True, help="Last Name not given!")

    def get(self):
        """ if user attempts to use get, he is instructed to use post """

        return ("Login required! Please make a POST /bucketlist_api/v1.0/auth/login with "
                "your username and password")

    def post(self):
        """ allows the user to log in using post """
        # get the details of the user
        username = request.form.get('username')
        password = request.form.get('password')
        result = ['The following fields cannot be empty:']
        user = {
            "username": username,
            "password": password
        }
        # if no username or password is given, an error message should be
        # returned
        for key, value in user.items():
            if value == '':
                result.append(key)
        if len(result) > 1:
            resp = ' '.join(result)
        else:
            # checks for the user in the database
            result_user = User.query.filter_by(username=username).first()
            # checks for the user password
            if result_user.check_password(password):
                # generates the token for the user
                token = result_user.generate_token()
                # gives message response
                resp = {'token': token,
                        'message': "You have logged in successfully"}, 200

            else:
                # message that is returned if user could not be logged in
                resp = "Could not log you in! Check your username and password and try again!"

        return resp


class BucketlistAPI(Resource):
    """ class resource that allows for the creation and retrieval of bucketlists """
    # sets authentication for the resource, requires user to be logged in
    decorators = [auth_token.login_required]

    def __init__(self):
        """ initializes the class variables """
        # gets number of pages
        self.page = request.args.get('page', 1, type=int)
        self.max_limit = 100
        # sets the minimum limit per page
        self.request_limit = request.args.get('limit', 2, type=int)
        self.limit = min(self.request_limit, self.max_limit)
        # gets the search term
        self.search_term = request.args.get('q', type=str)
        self.query_items = ''
        self.query = ''

    def post(self):
        """ allows the user to create a bucketlist using post """
        # gets the name given for the bucketlist
        name = str(request.data.get('name', ''))
        # if name has been given
        if name:
            # saves the bucketlist to the database
            bucketlist = Bucketlist(
                name=name, created_by=g.current_user.username, user_id=g.current_user.user_id)
            bucketlist.save()

            # display that no items have been created yet in method return
            item_object = 'No items yet!'

            # converts the response to json format
            response = jsonify({
                'id': bucketlist.bucketlist_id,
                'name': bucketlist.name,
                'created_by': g.current_user.username,
                'items': item_object,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified
            })
            response.status_code = 201
        else:
            # gives error response if no name has been given
            response = {'message': 'no name for the bucketlist has been given'}
        return response

    def get(self):
        """ get method that retrieves bucketlists and sets them in pages """

        if not self.search_term:
            # if no search term has been given
            # retrieves bucketlists as pages
            bucketlists_by_page = Bucketlist.query.filter_by(
                user_id=g.current_user.user_id).order_by(
                    Bucketlist.date_modified.desc()).paginate(
                        self.page, self.limit, error_out=True)

        else:
            # if a search term has been given
            # retrieves bucketlists as pages
            bucketlists_by_page = Bucketlist.query.filter_by(
                user_id=g.current_user.user_id).filter(Bucketlist.name.ilike(
                    '%' + self.search_term + '%')).order_by(
                        Bucketlist.date_modified.desc()).paginate(
                            self.page, self.limit, error_out=True)

        # if no bucketlists have been found and search term has been provided
        if not bucketlists_by_page.items and self.search_term:
            error_response = {'error': 'Not found',
                              'message': 'No results'}, 404

            # return the error response with its status code
            return error_response

        # if no bucketlists have been found
        if not bucketlists_by_page.items:
            error_response = {'error': 'Not found',
                              'message': 'No bucketlists have been added'}, 404

            # return the error response with its status code
            return error_response

        # checks if there's a next page of bucketlists
        if bucketlists_by_page.has_next:
            url_next = url_for(request.endpoint, page=self.page + 1,
                               limit=self.limit, query=self.search_term)
        else:
            # if there isn't a next page
            url_next = "Null"

        # checks if there is a previous page of bucketlists
        if bucketlists_by_page.has_prev:
            url_prev = (url_for(request.endpoint) +
                        "?q=" + str(self.search_term) +
                        "?page=" + str(self.page - 1) +
                        "&limit=" + str(self.limit) +
                        self.query.format(self.query_items))

        else:
            # if there isn't a previous page
            url_prev = "Null"

        # appends the result to its corresponding schema
        result = bucketlist_schema.dump(list(bucketlists_by_page.items))

        # returns the result with its status code
        return {"info": {"next_page": url_next,
                         "previous_page": url_prev,

                         "total_pages": bucketlists_by_page.pages},

                "bucketlists": result.data

                }, 200


class GetBucketlist(Resource):
    """ allows the user to retrieve a particular bucketlist by using its id """

    # sets authentication for the resource, requires user to be logged in and
    # token given
    decorators = [auth_token.login_required]

    def get(self, bucketlist_id):
        """ allows the user to retrieve the bucketlist by its id using get """

        # gets the bucketlist and its items and arranges it by pages
        bucketlists_by_page = Bucketlist.query.filter_by(
            bucketlist_id=bucketlist_id, user_id=g.current_user.user_id).order_by(
                Bucketlist.date_modified.desc()).paginate(
                    error_out=True)

        # if no bucketlists are found, an error message should be given
        if not bucketlists_by_page.items:
            error_response = {'error': 'Not found',
                              'message': 'No results'}, 404
            return error_response
        else:
            # attaches the result to its corresponding schema and returns it
            result = bucketlist_schema.dump(list(bucketlists_by_page.items))
        return {"bucketlist": result}, 200


class BucketlistItem(Resource):
    """ class resource that allows the user to create, edit and delete a bucketlist item """
    # sets authentication for the resource, requires user to be logged in and
    # token given
    decorators = [auth_token.login_required]

    def post(self, bucketlist_id):
        """ method that creates the bucketlist item """

        # gets the bucketlist item details
        name = request.form.get('name')
        description = request.form.get('description')

        # check if the bucketlist exists
        self.bucketlist = Bucketlist.query.filter_by(
            bucketlist_id=bucketlist_id, created_by=g.current_user.username).first()
        if not self.bucketlist:

            # Raise an HTTPException with a 404 not found status code
            response = jsonify({'message': 'Bucketlist does not exist!'})
            response.status_code = 404
        else:
            name = str(request.data.get('name', ''))
            if name:
                # stores the bucketlist item details in the database
                bucketlist_items = BucketlistItems(
                    name=name, bucketlist_id=bucketlist_id, description=description,
                    user_id=g.current_user.user_id, created_by=g.current_user.username)
                bucketlist_items.save()

                # get the saved bucketlist item to set as output
                bucketlist_created_item = BucketlistItems.query.filter_by(
                    name=name, created_by=g.current_user.username).first()

                # gives the result in json format with the status code
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
        """ allows the user to edit the bucketlist item using put method """

        # get the bucketlist item details
        name = request.form.get('name')
        description = request.form.get('description')
        done = request.form.get('done')

        # if item id has been given
        if item_id:

            # retrieve the bucketlist item from the database by its id
            edit_item = BucketlistItems.query.filter_by(
                item_id=item_id, bucketlist_id=bucketlist_id,
                created_by=g.current_user.username).first()

            # if name remains unchanged, revert to the default one
            if name == '':
                name = edit_item.name

            # if description remains unchanged, revert to the default one
            if description == '':
                description = edit_item.description

            # if done field remains unchanged, revert to the default one
            if done == '':
                done = edit_item.done

            # attach the items to the query
            edit_item.name = name
            edit_item.description = description
            edit_item.done = done

            # saves the items
            edit_item.save()

            # gives the response in json format with the status code
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
        """ deletes the bucketlist item """

        # gets the bucketlist item from the database by using its id given
        delete_item = BucketlistItems.query.filter_by(
            item_id=item_id, created_by=g.current_user.username).first()

        # message that is returned if the bucketlist item does not exist
        # returns with status code
        if not delete_item:
            response = jsonify({'message': 'Bucketlist item does not exist!'})
            response.status_code = 404
        else:
            # captures the name of the deleted bucketlist item
            name = delete_item.name
            # deletes the item
            delete_item.delete()
            # returns the message that the particular item was deleted successfully
            response = {
                "message": "bucketlist item {} deleted successfully".format(name)
            }, 200

        return response


class UpdateBucketlist(Resource):
    """ class resource that allows the user to edit and delete a bucketlist """ 
    # sets authentication for the resource, requires user to be logged in and
    # token given
    decorators = [auth_token.login_required]

    def delete(self, bucketlist_id):
        """ method to delete the bucketlist """

        # searches for the particular bucketlist in the database by using its id
        delete_bucketlist = Bucketlist.query.filter_by(
            bucketlist_id=bucketlist_id, created_by=g.current_user.username).first()

        # if no bucketlist has been found, return an error message with the status code
        if not delete_bucketlist:
            response = jsonify({'message': 'Bucketlist item does not exist!'})
            response.status_code = 404
        else:
            # capture the name of the bucketlist to be deleted
            name = delete_bucketlist.name
            delete_bucketlist.delete()

            # return the message of successful deletion along with the status code
            return {
                "message": "bucketlist item {} deleted successfully".format(name)
            }, 200

    def put(self, bucketlist_id):
        """ method to edit the bucketlist """

        # gets the name change of the bucketlist
        name = request.form.get('name')

        # retrieves the bucketlist by id
        if bucketlist_id:
            edit_bucketlist = Bucketlist.query.filter_by(
                bucketlist_id=bucketlist_id, created_by=g.current_user.username).first()

            # if no name change has been given, default to the previous one
            if name == '':
                name = edit_bucketlist.name

            # stores the new name in a variable
            edit_bucketlist.name = name

            # saves the name change to the database
            edit_bucketlist.save()

            # returns the response in json format with the status code
            response = jsonify({
                'message': 'Bucketlist Updated Successfully',
                'id': edit_bucketlist.bucketlist_id,
                'name': edit_bucketlist.name,
                'date_created': edit_bucketlist.date_created,
                'date_modified': edit_bucketlist.date_modified,
                'created_by': edit_bucketlist.created_by
            })
            response.status_code = 201

            return response
