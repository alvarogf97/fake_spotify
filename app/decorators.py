from functools import wraps
from flask import session, abort, request
import logging


def login_required(f):
    """ Flask login decorator """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('current_user') is None:
            abort(401)  # UNAUTHORIZED
        return f(*args, **kwargs)
    return decorated_function
