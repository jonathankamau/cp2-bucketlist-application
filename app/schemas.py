from marshmallow import Schema, fields, validate
from flask_marshmallow import Marshmallow

ma = Marshmallow()


class RegisterUserSchema(Schema):
    firstname = fields.String(required=True, load_only=True, validate=[validate.Length(min=1, max=64),
                                                                       validate.Regexp(r"[a-zA-Z]*$",
                                                                                       error=("Firstname must be made up of letters!"))],
                              error_messages={'required': 'firstname cannot be blank'})
    lastname = fields.String(required=True, load_only=True, validate=[validate.Length(min=1, max=64)],
                             error_messages={'required': 'lastname cannot be blank'})
    username = fields.String(required=True, load_only=True, validate=[validate.Length(min=1, max=64)],
                             error_messages={'required': 'username cannot be blank'})
    password = fields.String(required=True, load_only=True, validate=[validate.Length(min=8)],
                             error_messages={'required': 'password cannot be blank'})


class UserLoginSchema(Schema):
    username = fields.String(required=True, load_only=True, validate=[validate.Length(min=1, max=64),
                                                                      validate.Regexp(r"[a-zA-Z]*$",
                                                                                      error=("Username must be made up of letters!"))])
    password = fields.String(required=True, load_only=True, validate=[validate.Length(min=8)],
                             error_messages={'required': 'password cannot be blank'})


class BucketlistItemsSchema(Schema):
    item_id = fields.Integer(dump_only=True)
    name = fields.String(required=True, dump_only=True,
                         error_messages={'required': 'bucketlist name cannot be blank'})
    description = fields.String()
    created_by = fields.String(dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime(dump_only=True)


class BucketlistSchema(ma.ModelSchema):
    name = fields.String(required=True, dump_only=True,
                         error_messages={'required': 'bucketlist name cannot be blank'})
    bucketlist_id = fields.Integer(dump_only=True)
    bucketlist_items = fields.Nested(
        BucketlistItemsSchema, dump_only=True, many=True)
    created_by = fields.String(dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime(dump_only=True)
    #url = fields.Method('get_url', dump_only=True)

class FlaskBucketlistSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ('name', 'bucketlist_id', 'bucketlist_items',
                  'created_by', 'date_created', 'date_modified')

#flask_bucketlist = FlaskBucketlistSchema(many=True)
reg_schema = RegisterUserSchema()
user_login = UserLoginSchema()
bucketlist_schema = BucketlistSchema(many=True)
bucketlist_items = BucketlistItemsSchema()
