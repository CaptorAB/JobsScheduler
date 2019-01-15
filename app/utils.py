import logging
import http.client
from functools import wraps
import flask
import jsonschema


def validate_input(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            # GET does not need validation
            if flask.request.method in ['POST', 'PUT', 'DELETE']:
                try:
                    data = flask.request.get_json()
                except Exception as e:
                    return {"error": 'Could not decode json'}, http.client.BAD_REQUEST
                try:
                    jsonschema.validate(data, schema)
                except jsonschema.ValidationError as e:
                    logging.debug({"error": str(e)})
                    return {"error": str(e)}, http.client.BAD_REQUEST
            return f(*args, **kw)

        return wrapper

    return decorator


def validate_output(schema):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Invoke the wrapped function first
            retval = func(*args, **kwargs)
            # Now do something here with retval

            assert len(retval) == 2, "need both data and status_code"
            data = retval[0]
            status_code = retval[1]
            if (status_code / 100) == 2:
                try:
                    jsonschema.validate(data, schema)
                except jsonschema.ValidationError as e:
                    print(e)
                    logging.debug({"error": str(e)})
                    return {"error": str(e)}, http.client.BAD_REQUEST

            return retval

        return wrapper

    return decorator

