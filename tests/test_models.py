import unittest
import os
import json

from werkzeug.security import generate_password_hash, check_password_hash

from app import create_app, db
from app.models import User, Bucketlist, BucketlistItems

class ModelTests(unittest.TestCase):
    """This class represents test case for bucketlist configurations"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

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
            self.current_user = User('John','Kamau', 'kamjon', 'kamjon123')
    def test_get_password(self):
        password = self.register_data['password']
        self.assertTrue(check_password_hash(self.current_user.get_password, password))

    