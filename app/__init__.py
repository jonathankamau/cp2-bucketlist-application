import os

from flask_api import FlaskAPI
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app_settings = os.getenv(
    'APP_SETTINGS',
    'instance.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)


# # local imports
# from instance.config import app_config

# #app = FlaskAPI(__name__)
# bcrypt = Bcrypt()
# db = SQLAlchemy()
# # db variable initialization
# #db = SQLAlchemy()

# def create_app(config_name):
#     app = FlaskAPI(__name__, instance_relative_config=True)
#     app.config.from_object(app_config[config_name])
#     app.config.from_pyfile('config.py')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     db.init_app(app)
#     return app
