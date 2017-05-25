import unittest
import os
import json
import time
from flask_testing import TestCase
from werkzeug.security import generate_password_hash, check_password_hash

from app import create_app, db
from app.models import User, Bucketlist, BucketlistItems
from app.resources import UserLogin


class ResourceTests(unittest.TestCase):
    """This class represents test case for bucketlist methods"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Dance in the moonlight'}
        self.bucketlist_item = {'name':'sing in the moonlight',
                                'description':'singing crazy songs'}
        self.user = User
        self.userlogin = UserLogin()
        self.bucketlists = Bucketlist
        self.bucketlistitems = BucketlistItems
        self.register_data = {'firstname': 'John',
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
            self.register_response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                                        data=self.register_data)
            self.login_response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                                     data=self.login_data)
            result = json.loads(self.login_response.data)
            self.token = result['token']

    def test_can_register_user(self):
        """ tests if the API can register a user """
        self.assertEqual(self.register_response.status_code, 201)
        self.assertIn('You have registered successfully',
                      str(self.register_response.data), msg="Not registered")

    def test_bucketlist_can_login_user(self):
        """ Test if the API can log in a user"""
        self.assertEqual(self.register_response.status_code, 201)
        self.assertEqual(self.login_response.status_code, 200)
        self.assertIn('You have logged in successfully',
                      str(self.login_response.data), msg="Not logged in")

    def test_bucketlist_creation(self):
        """Test if API can create a bucketlist (POST request)"""
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist, 
            headers={'Authorization': self.token})

        self.assertEqual(response.status_code, 201)
        self.assertIn('Dance in the moonlight', str(
            response.data), msg="Bucketlist not created")

    def test_api_get_all_bucketlists(self):
        """Test if API can get all bucketlists for the user (GET request)."""
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist,
            headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 201)
        response = self.client().get('/bucketlist_api/v1.0/bucketlists/',
                                     headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Dance in the moonlight', str(
            response.data), msg="Bucketlist not retrieved")

    def test_api_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist,
            headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 201)
        result = self.client().get(
            '/bucketlist_api/v1.0/bucketlists/1', headers={'Authorization': self.token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('Dance in the moonlight', str(result.data),
                      msg="Could not retrieve bucketlist")

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data={'name': 'Go to mars'}, headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 201)
        response = self.client().put(
            '/bucketlist_api/v1.0/bucketlists/1',
            data={
                "name": "Go to mars and meet aliens!"
            }, headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 200)
        results = self.client().get('/bucketlist_api/v1.0/bucketlists/1',
                                    headers={'Authorization': self.token})
        self.assertIn('meet aliens!', str(results.data),
                      msg="Bucketlist could not be edited")

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data={'name': 'Go to mars'}, headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 201)
        res = self.client().delete('/bucketlist_api/v1.0/bucketlists/1',
                                   headers={'Authorization': self.token})
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/bucketlist_api/v1.0/bucketlists/1/',
                                   headers={'Authorization': self.token})
        self.assertEqual(result.status_code, 404,
                         msg="bucketlist still exists")

    def test_generate_token(self):
        """ tests if the API can generate a token for the user """
        registration_response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                                   data=self.register_data)

        login_response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                            data=self.login_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('token', str(login_response.data),
                      msg='token not generated!')

    def test_get_method_return_when_registering_user(self):
        """ tests what is returned when user attempts to register using get """
        response = self.client().get('/bucketlist_api/v1.0/auth/register',
                                     data=self.register_data)
        actual_response = "To Register, please make a POST"
        self.assertIn(actual_response, str(response.data),
                      msg="Wrong response given")

    def test_user_already_exists(self):
        """ tests if the user already exists """
        self.client().post('/bucketlist_api/v1.0/auth/register',
                           data=self.register_data)

        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.register_data)
        self.assertEqual(response.status_code, 409)
        self.assertIn("User already exists!", str(response.data),
                      msg="Does not detect user!")

    def test_check_password_hash(self):
        """ tests if the password is hashed """
        self.client().post('/bucketlist_api/v1.0/auth/register', data=self.register_data)
        password = 'kamjon123'
        self.client().post('/bucketlist_api/v1.0/auth/login',
                           data={'username': 'kamjon',
                                 'password': password
                                })
        response = check_password_hash(generate_password_hash(
            password), self.register_data['password'])
        self.assertTrue(response, msg="Passwords don't match")

    def test_invalid_token(self):
        """ checks if the token is invalid """
        token = self.token + 'erhjddshehsjdjsdj'
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data={'name': 'Go to mars'}, headers={'Authorization': token})
        self.assertEqual(response.status_code, 401)
        self.assertIn("Please send a valid authentication token",
                      str(response.data), msg="Not Invalid")

    def test_expired_token(self):
        """ checks if the token has expired """
        result_user = User('John', 'Kamau', 'kamjon', 'kamjon123')
        token = result_user.generate_token(1)
        time.sleep(3)
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data={'name': 'Go to mars'}, headers={'Authorization': token})
        self.assertIn("Please send a valid authentication token",
                      str(response.data), msg="Not Expired")

    def test_for_registration_validation(self):
        """ tests if validation during registration works """
        register_data = {'firstname': '1234',
                         'lastname': '#$%',
                         'username': '',
                         'password': 'kamjon123'}
        register_response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                               data=register_data)

        self.assertIn("errors", str(register_response.data))

    def test_for_login_with_get(self):
        """ tests the response when someone attempts login with get """
        login_response = self.client().get('/bucketlist_api/v1.0/auth/login',
                                           data=self.login_data)

        self.assertIn("Please make a POST /bucketlist_api/v1.0/auth/login",
                      str(login_response.data))

    def test_for_login_with_wrong_password(self):
        """ tests the response if someone logs in with wrong password """
        login_data = {'username': 'kamjon',
                      'password': 'kam123'}
        login_response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                            data=login_data)

        self.assertIn("Could not log you in!", str(login_response.data))

    def test_if_no_bucketlist_exists(self):
        """ tests what error message is returned if no bucketlist exists """
        response = self.client().get(
            '/bucketlist_api/v1.0/bucketlists/',
            data=self.bucketlist, headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 404)
        self.assertIn('Not found', str(response.data))

    def test_if_no_bucketlist_for_bucketlistitem(self):
        """ tests if there is no bucketlist for bucketlist item being sought """
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/8/items/',
            data={'name': 'Go to mars'}, headers={'Authorization': self.token})

        self.assertEqual(response.status_code, 404)
        self.assertIn('Bucketlist does not exist!', str(response.data))

    def test_get_bucketlistitems_for_bucketlist(self):
        """Test if API can get all bucketlists items for a particular bucketlist (GET request)."""
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist,
            headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 201)
        self.client().post('/bucketlist_api/v1.0/bucketlists/1/items/', data=self.bucketlist_item,
                           headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 201)
        item_response = self.client().get('/bucketlist_api/v1.0/bucketlists/1/items/',
                                          headers={'Authorization': self.token})
        self.assertEqual(item_response.status_code, 200)
        self.assertIn('sing in the moonlight', str(
            item_response.data), msg="Bucketlist items not retrieved")

    def test_get_bucketlistitems_for_bucketlist_by_id(self):
        """Test if API can get a particular bucketlists item by id (GET request)."""
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist,
            headers={'Authorization': self.token})
        self.assertEqual(response.status_code, 201)
        item_reg_response = self.client().post('/bucketlist_api/v1.0/bucketlists/1/items/',
                                               data=self.bucketlist_item,
                                               headers={'Authorization': self.token})
        self.assertEqual(item_reg_response.status_code, 201)
        result = self.client().get('/bucketlist_api/v1.0/bucketlists/1/items/1',
                                   headers={'Authorization': self.token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('sing in the moonlight', str(result.data),
                      msg="Could not retrieve bucketlist item")

    def test_if_bucketlist_exists_for_bucketlistitem(self):
        """ test if the bucketlist exists for the bucketlist item """
        bucket_response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data=self.bucketlist, headers={'Authorization': self.token})
        self.assertEqual(bucket_response.status_code, 201)
        item_response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items/',
            data={'name': 'Go to mars'}, headers={'Authorization': self.token})
        self.assertEqual(item_response.status_code, 201)
        self.assertIn('Bucketlist Item Created Successfully', str(item_response.data))

    def test_update_bucketlistitem(self):
        """ tests if the bucketlist item was successfully updated """
        bucket_response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data=self.bucketlist, headers={'Authorization': self.token})
        self.assertEqual(bucket_response.status_code, 201)
        item_response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items/',
            data={'name': 'Go to mars'}, headers={'Authorization': self.token})
        self.assertEqual(item_response.status_code, 201)
        update_response = self.client().put(
            '/bucketlist_api/v1.0/bucketlists/1/items/1',
            data={'name': 'Go to mercury'}, headers={'Authorization': self.token})
        self.assertEqual(update_response.status_code, 200)
        self.assertIn('Bucketlist Item Updated Successfully', str(update_response.data))

    def test_bucketlistitem_deletion(self):
        """ tests if the bucketlist item was successfully deleted """
        bucket_response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data=self.bucketlist, headers={'Authorization': self.token})
        self.assertEqual(bucket_response.status_code, 201)
        item_response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items/',
            data={'name': 'Go to mars'}, headers={'Authorization': self.token})
        self.assertEqual(item_response.status_code, 201)
        delete_response = self.client().delete(
            '/bucketlist_api/v1.0/bucketlists/1/items/1',
            headers={'Authorization': self.token})
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn('deleted successfully', str(delete_response.data))

    def test_bucketlistitem_does_not_exist(self):
        """ tests the response if bucketlist item does not exist """
        bucket_response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/',
            data=self.bucketlist, headers={'Authorization': self.token})
        self.assertEqual(bucket_response.status_code, 201)
        item_response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items/',
            data={'name': 'Go to mars'}, headers={'Authorization': self.token})
        self.assertEqual(item_response.status_code, 201)
        delete_response = self.client().delete(
            '/bucketlist_api/v1.0/bucketlists/1/items/9',
            headers={'Authorization': self.token})
        self.assertEqual(delete_response.status_code, 404)
        self.assertIn('Bucketlist item does not exist!', str(delete_response.data))


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
