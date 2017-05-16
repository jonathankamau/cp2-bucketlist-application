import unittest
import os
import json

from flask_testing import TestCase
from werkzeug.security import generate_password_hash, check_password_hash

from app import create_app, db
from app.models import User, Bucketlist, BucketlistItems



class ResourceTests(unittest.TestCase):
    """This class represents test case for bucketlist methods"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Dance in the moonlight'}
        self.user = User
        self.bucketlists = Bucketlist
        self.bucketlistitems = BucketlistItems
        self.register_data = {'firstname':'John',
                              'lastname': 'Kamau',
                              'username': 'kamjon',
                              'password': 'kamjon123'
                             }
        self.login_data = {'username': 'kamjon',
                           'password': 'kamjon123'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_can_register_user(self):
        """ tests if the API can register a user """
        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.register_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('You have registered successfully', str(response.data))

    def test_bucketlist_can_login_user(self):
        """ Test if the API can log in a user"""
        registration_response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                                   data=self.register_data)
        self.assertEqual(registration_response.status_code, 200)
        login_response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                            data=self.login_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('You have logged in successfully',
                      str(login_response.data))

    def test_bucketlist_creation(self):
        """Test if API can create a bucketlist (POST request)"""
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Dance in the moonlight', str(response.data))

    def test_api_can_get_all_bucketlists(self):
        """Test if API can get a bucketlist (GET request)."""
        res = self.client().post('/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/bucketlist_api/v1.0/bucketlists/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Dance in the moonlight', str(res.data))

    def test_api_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        rv = self.client().post('/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/bucketlist_api/v1.0/bucketlists/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Dance in the moonlight', str(result.data))

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        rv = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data={'name': 'Go to mars'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/bucketlists/1',
            data={
                "name": "Go to mars and meet aliens!"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/bucketlist_api/v1.0/bucketlists/1')
        self.assertIn('meet aliens!', str(results.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        rv = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data={'name': 'Go to mars'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/bucketlist_api/v1.0/bucketlists/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/bucketlist_api/v1.0/bucketlists/1')
        self.assertEqual(result.status_code, 404)

    def test_generate_token(self):
        """ tests if the API can generate a token for the user """
        registration_response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                                   data=self.register_data)
        self.assertEqual(registration_response.status_code, 200)
        login_response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                            data=self.login_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('token', str(login_response.data), msg='token not generated!')

    def test_get_password(self):
        """ tests the method get_password if it fetches the users password from db """
        registration_response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                                   data=self.register_data)
        self.assertEqual(registration_response.status_code, 200)
        login_response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                            data=self.login_data)
        self.assertEqual(login_response.status_code, 200)
        hashed_password = generate_password_hash(self.login_data['password'])
        got_password = self.user.get_password
        self.assertEqual(hashed_password, got_password,
                         msg='Passwords not equal!')

    def test_get_method_return_when_registering_user(self):
        """ tests what is returned when user attempts to register using get """
        response = self.client().get('/bucketlist_api/v1.0/auth/register',
                                     data=self.register_data)
        actual_response = "To Register please make a POST"
        self.assertIn(actual_response, str(response.data),
                      msg="Wrong response given")

    def test_user_already_exists(self):
        """ tests if the user already exists """
        registration_response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                                   data=self.register_data)
        self.assertEqual(registration_response.status_code, 200)
        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.register_data)
        self.assertIn("User already exists!", str(response.data),
                      msg="Does not detect user!")

    def test_check_password_hash(self):
        """ tests if the password is hashed """
        data = {'firstname': 'John',
                'lastname': 'Kamau',
                'username': 'kamjon',
                'password': 'kamjon123'
               }
        self.client().post('/bucketlist_api/v1.0/auth/register', data=data)
        password = 'kamjon123'
        self.client().post('/bucketlist_api/v1.0/auth/login',
                           data={'username': 'kamjon',
                                 'password': password
                                })
        response = check_password_hash(data['password'], password)
        self.assertTrue(response, msg="Passwords don't match")

    def test_empty_username_or_password(self):
        """ tests if username or password is empty """
        response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                      data={'username': '',
                                            'password': ''
                                           })

        self.assertIn("The following fields cannot be empty",
                      str(response.data), msg="Error message not given")

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
