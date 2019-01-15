import os
import unittest
import datetime
import time
import base64
import jwt as pyjwt

from app.main import create_app_for_testing


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app_for_testing()
        self.app.testing = True
        self.test_client = self.app.test_client()

    def tearDown(self):
        self.app.db.delete_db()

    def create_token(self):
        d2 = datetime.date(2018, 6, 1)
        nbf = int(time.mktime(d2.timetuple()))

        d1 = datetime.date(2028, 6, 1)
        exp = int(time.mktime(d1.timetuple()))

        data = {'unique_name': '201801011234',
                'db': 'prod',
                'aud': self.app.config['JWT_AUDIENCE'],
                'exp': exp,
                'nbf': nbf}

        # return pyjwt.encode(data, base64.b64decode(self.app.config['JWT_KEY']), algorithm='HS256')
        return pyjwt.encode(data, self.app.config['JWT_KEY'], algorithm='HS256')
