from functools import wraps
from flask import request
import jwt as pyjwt
import base64
import http.client
from pprint import pprint

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
            return {"error": str(e)}, http.client.UNAUTHORIZED
        ctx_stack.top.jwt = jwt_data
        return fn(*args, **kwargs)

    return wrapper


def decode_jwt(encoded_token):
    """
    Returns the decoded token from an encoded one. This does all the checks
    to insure that the decoded token is valid before returning it.
    """
    secret = current_app.config['JWT_KEY']
    audience = current_app.config['JWT_AUDIENCE']
    return pyjwt.decode(encoded_token, secret, algorithms=['HS256'], audience=audience)


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
