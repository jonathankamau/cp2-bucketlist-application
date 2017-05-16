import os

import jwt
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


class Helper:

    def generate_token(self, user):
        secret_key = os.getenv('SECRET')
        jwt_string = jwt.encode(user, secret_key)

        return jwt_string

    