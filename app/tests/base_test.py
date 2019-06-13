import os
import unittest
import datetime
import time
import jwt
from jwt.algorithms import RSAAlgorithm

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

        payload = {'unique_name': '201801011234',
                   'db': 'prod',
                   'aud': self.app.config['JWT_AUDIENCE'],
                   'exp': exp,
                   'nbf': nbf}

        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unittest.private.pem")
        with open(file_path, 'rb') as file_handle:
            pem = file_handle.read()

        token = jwt.encode(payload=payload, key=pem, headers={"kid": "unittest"}, algorithm="RS256")

        return token
