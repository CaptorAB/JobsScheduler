import flask
from flask_cors import CORS
from flask.testing import FlaskClient
from pymongo import MongoClient

from app.api import api_bp
from app.slash import slash_bp
from app.db import DB


def base_create_app():
    flask_app = flask.Flask(__name__)
    flask_app.register_blueprint(slash_bp, url_prefix='/')
    flask_app.register_blueprint(api_bp, url_prefix='/api')
    return flask_app


def create_app():
    flask_app = base_create_app()
    CORS(flask_app)
    from app import settings as settings
    flask_app.config['JWT_KEY'] = settings.JWT_KEY
    flask_app.config['JWT_AUDIENCE'] = settings.JWT_AUDIENCE
    client = MongoClient()
    db = client.local
    flask_app.db = DB(db=db)
    return flask_app


def create_app_for_testing():
    flask_app = base_create_app()
    from app import test_settings as settings
    flask_app.config['JWT_KEY'] = settings.JWT_KEY
    flask_app.config['JWT_AUDIENCE'] = settings.JWT_AUDIENCE
    import mongomock
    db = mongomock.MongoClient().db
    flask_app.db = DB(db=db)
    flask_app.test_client_class = FlaskClient
    flask_app.debug = True
    flask_app.testing = True
    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, ssl_context='adhoc')
