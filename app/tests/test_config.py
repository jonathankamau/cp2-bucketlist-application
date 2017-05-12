import unittest
import bucketlist.instance.config

from flask import current_app
from flask_testing import TestCase

from app import app

class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('instance.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:@localhost/bucketlist'
        )


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('application.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:@localhost/bucketlist_test'
        )
