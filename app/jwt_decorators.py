import datetime
import json
import logging
from pprint import pformat

from functools import wraps
from flask import request
import requests

import jwt
from jwt.algorithms import RSAAlgorithm
import http.client

try:
    from flask import _app_ctx_stack as ctx_stack
except ImportError:  # pragma: no cover
    from flask import _request_ctx_stack as ctx_stack

from flask import current_app


class FlaskJWTException(Exception):
    """
    Base except which all flask_jwt_simple errors extend
    """
    pass


class InvalidHeaderError(FlaskJWTException):
    """
    An error raised when the expected header format does not match what was received
    """
    pass


class NoAuthorizationError(FlaskJWTException):
    """
    An error raised when no JWT was found when a protected endpoint was accessed
    """
    pass


class NoKeyMatchingKidFound(FlaskJWTException):
    pass


class MissingRequiredScopeError(FlaskJWTException):
    pass


def get_jwks():
    jwks = current_app.db.get_jwks()

    if not jwks or \
            "last_modified" in jwks and jwks["last_modified"] < datetime.datetime.utcnow() - datetime.timedelta(
        minutes=20):
        jwks_uri = current_app.config['JWKS_URI']

        if jwks_uri.startswith("file://"):
            file_path = jwks_uri.split("file://")[1];
            with open(file_path, 'rb') as file_handle:
                jwks = json.load(file_handle)
        else:
            jwks = requests.get(jwks_uri, verify=False, timeout=10).json()

        jwks = current_app.db.put_jwks(jwks)

    return jwks


def jwt_required(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid JWT before calling the actual view.

    :param fn: The view function to decorate
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            jwt_data = _decode_jwt_from_headers()
        except Exception as e:
            logging.exception("jwt_required()")
            return {"error": str(e)}, http.client.UNAUTHORIZED
        ctx_stack.top.jwt = jwt_data
        return fn(*args, **kwargs)

    return wrapper


def decode_jwt(encoded_token):
    """
    Returns the decoded token from an encoded one. This does all the checks
    to insure that the decoded token is valid before returning it.
    """
    audience = current_app.config['JWT_AUDIENCE']
    required_scopes = current_app.config['JWT_REQUIRED_SCOPES']
    header = jwt.get_unverified_header(encoded_token)
    kid = header["kid"]
    keys = get_jwks()["keys"]
    keys = {key["kid"]: key for key in keys}
    if kid not in keys:
        msg = "No key matching kid: {} found".format(kid)
        raise NoKeyMatchingKidFound(msg)

    public_key = RSAAlgorithm.from_jwk(json.dumps(keys[kid]))

    decoded = jwt.decode(encoded_token, key=public_key, algorithms=['RS256'], audience=audience)

    if len(required_scopes) > 0:
        if "scopes" not in decoded:
            msg = "Missing required scopes: {}".format(pformat(required_scopes))
            raise MissingRequiredScopeError(msg)
        else:
            scopes = decoded["scopes"]
            for required_scope in required_scopes:
                if required_scope not in scopes:
                    msg = "Missing required scope: {}".format(pformat(required_scope))
                    raise MissingRequiredScopeError(msg)
    return decoded


def _decode_jwt_from_headers():
    header_name = "Authorization"
    header_type = "Bearer"

    # Verify we have the auth header
    jwt_header = request.headers.get(header_name, None)
    if not jwt_header:
        msg = "Missing {} Header".format(header_name)
        raise NoAuthorizationError(msg)

    # Make sure the header is in a valid format that we are expecting, ie
    # <HeaderName>: <HeaderType(optional)> <JWT>
    parts = jwt_header.split()
    if not header_type:
        if len(parts) != 1:
            msg = "Bad {} header. Expected value '<JWT>'".format(header_name)
            raise InvalidHeaderError(msg)
        token = parts[0]
    else:
        if parts[0] != header_type or len(parts) != 2:
            msg = "Bad {} header. Expected value '{} <JWT>'".format(header_name, header_type)
            raise InvalidHeaderError(msg)
        token = parts[1]

    return decode_jwt(encoded_token=token)
