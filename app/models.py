import datetime
import os

from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"
    # database fields
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    bucketlists = db.relationship('Bucketlist', order_by='Bucketlist.bucketlist_id')

    def __init__(self, firstname, lastname, username, password):
        """ initialize the model fields """
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = generate_password_hash(password)
        self.registered_on = datetime.datetime.now()

    @property
    def get_password(self):
        """ retrieves the password """
        return self.password

    @property
    def get_id(self):
        """ retrieves the user id """
        return self.user_id


    def check_password(self, password):
        """ upon login, checks if the password given is same as that in the database """
        if check_password_hash(self.password, password):
            return True
        return False

    def save(self):
        """ saves the user details to the database """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, expiration=6000):
        serial = Serializer(os.getenv('SECRET'), expires_in=expiration)
        return "Bearer "+serial.dumps({'id': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        serial = Serializer(os.getenv('SECRET'))
        try:
            data = serial.loads(token)

        except SignatureExpired:
            return "Expired Token!" # valid token, but expired
        except BadSignature:
            return "Invalid Token!" # invalid token
        user = User.query.get(data['id'])
        return user

class Bucketlist(db.Model):
    """This class represents the bucketlist table, it maps to the table"""

    __tablename__ = 'bucketlists'

    bucketlist_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_by = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    user = db.relationship('User')
    bucketlist_items = db.relationship('BucketlistItems', backref='items', lazy='select', order_by="desc(BucketlistItems.date_modified)")

    def __init__(self, name, user_id, created_by):
        """initialize with name of bucketlist and author."""
        self.name = name
        self.created_by = created_by
        self.user_id = user_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Bucketlist.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist: {}>".format(self.name)

class BucketlistItems(db.Model):
    """This class represents the bucketlist items table, it maps to the table"""
    __tablename__ = 'bucketlist_items'

    item_id = db.Column(db.Integer, primary_key=True)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.bucketlist_id'))
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    done = db.Column(db.Boolean, unique=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_by = db.Column(db.String(255))

    def __init__(self, name, bucketlist_id, user_id, description, created_by):
        """initialize with name."""
        self.name = name
        self.bucketlist_id = bucketlist_id
        self.description = description
        self.created_by = created_by
        self.user_id = user_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Items: {}>".format(self.name)
