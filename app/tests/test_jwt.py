import unittest
import jwt as pyjwt
from unittest import skip


class TestJWT(unittest.TestCase):

    @skip('Not an automatic test. Used for debugging jwt')
    def test_jwt(self):
        from app import settings
        secret = settings.JWT_KEY
        audience = settings.JWT_AUDIENCE
        encoded_token = "CENSORED"
        pyjwt.decode(encoded_token, secret, algorithms=['HS256'], audience=audience)
