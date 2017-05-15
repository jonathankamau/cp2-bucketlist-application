import unittest
import os
import sys
import json

from flask import current_app
from flask_testing import TestCase

from  app import create_app, db

class BucketlistTests(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Dance in the moonlight'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()
    def test_bucketlist_api_can_register_user(self):
        """Test if API can register a user"""
        response = (self.client().post('/bucketlist_api/v1.0/auth/register',
                                       data={'firstname':'John',
                                             'lastname': 'Kamau',
                                             'username': 'kamjon',
                                             'password': 'kamjon123'
                                            }))

        self.assertEqual(response.status_code, 200)
        self.assertIn('You have registered successfully', str(response.data))

    def test_bucketlist_can_login_user(self):
        """ Test if the API can log in a user"""
        self.client().post('/bucketlist_api/v1.0/auth/register',
                           data={'firstname':'John',
                                 'lastname': 'Kamau',
                                 'username': 'kamjon',
                                 'password': 'kamjon123'
                                })
        response = (self.client().post('/bucketlist_api/v1.0/auth/login',
                                       data={'username': 'kamjon',
                                             'password': 'kamjon123'
                                            }))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You have logged in successfully', str(response.data))

    def test_bucketlist_creation(self):
        """Test if API can create a bucketlist (POST request)"""
        response = self.client().post('/bucketlist_api/v1.0/bucketlists/', data=self.bucketlist)
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

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()