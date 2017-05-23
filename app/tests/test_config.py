import unittest
import os
import json

from flask_testing import TestCase

from app import create_app, db
from app.models import User, Bucketlist, BucketlistItems

class ConfigTests(unittest.TestCase):
    """This class represents test case for bucketlist configurations"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

    def test_database_uri(self):
        """ tests for db url """
        self.assertTrue(
            self.app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://localhost/bucketlist')

    def test_flask_config(self):
        """ check for flask configuration """
        self.assertTrue(self.app.config['FLASK_CONFIG'] == 'testing', msg="Does not exist")

    def test_secret_key(self):
        """ tests for secret key, if it exists """
        self.assertTrue(self.app.config['SECRET'] == 'aping&zk4&6&k8o5s9', msg="Does not exist")

    def test_sqlalchemy_track_modifications(self):
        """ tests if sqlalchemy track modifications is false """
        self.assertTrue(
            self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False, msg="Does not exist")
    