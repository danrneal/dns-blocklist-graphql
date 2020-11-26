"""Logic for authenticating users using Authorization header."""

import base64
import binascii
from functools import wraps

from flask import request
from graphql import GraphQLError

from models import User


def basic_auth(f):
    """A decorator to authenticate users using basic authentication.

    Args:
        f: A fcn to decorate
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        auth = request.headers.get("Authorization", None)
        if auth is None:
            raise GraphQLError("Authorization header is missing")

        if not auth.startswith("Basic "):
            raise GraphQLError("Invalid Authorization header")

        auth = auth.replace("Basic ", "", 1)
        try:
            auth = base64.b64decode(auth).decode("utf-8")
        except binascii.Error:
            raise GraphQLError("Unable to decode Authorization header")

        auth = auth.split(":", 1)
        if len(auth) < 2:
            raise GraphQLError("Password is missing from Authorization header")

        username, password = auth
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            raise GraphQLError("Invalid username and/or password")

        return f(*args, **kwargs)

    return decorator
