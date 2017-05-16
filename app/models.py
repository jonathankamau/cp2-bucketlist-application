import datetime

from ..app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    bucketlists = db.relationship('Bucketlist', order_by='Bucketlist.bucketlist_id')

    def __init__(self, firstname, lastname, username, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = generate_password_hash(password)
        self.registered_on = datetime.datetime.now()

    @property
    def get_password(self):
        return self.password

    @property
    def get_id(self):
        return self.user_id
    
    # def set_password(self, password):
    #     self.password = generate_password_hash(password)

    def check_password(self, password):
        if check_password_hash(self.password, password):
            return True
        return False

    def save(self):
        db.session.add(self)
        db.session.commit()

class Session(db.Model):
    """Maps to session table """
    __tablename__ = 'sessions'
    user_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256))

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Bucketlist(db.Model):
    """This class represents the bucketlist table, it maps to the table"""

    __tablename__ = 'bucketlists'

    bucketlist_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    #bucketlist_items = db.relationship('BucketlistItems', backref=db.backref('bucketlists'))
    user = db.relationship('User')
    bucketlist_items = db.relationship('BucketlistItems', backref='items', lazy='select')

    def __init__(self, name, created_by):
        """initialize with name of bucketlist and author."""
        self.name = name
        self.created_by = created_by

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
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    done = db.Column(db.Boolean, unique=False, default=False)

    def __init__(self, name, created_by):
        """initialize with name."""
        self.name = name
        self.created_by = created_by

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Items: {}>".format(self.name)