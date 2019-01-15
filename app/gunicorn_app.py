"""
This is intended for starting the app with
gunicorn --certfile file.crt --keyfile file.key -b 0.0.0.0:443 app.gunicorn_app:app


This due to starting a production server with flask development server is not advised.
"""

import os

from app.main import create_app

try:
    VERSION = os.environ['VERSION']
except:
    VERSION = 'DEV'

app = create_app()
