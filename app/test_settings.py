import os

JWT_AUDIENCE = "unittest"

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "jwks.json")
JWKS_URI = "file://" + file_path

JWT_REQUIRED_SCOPES = []