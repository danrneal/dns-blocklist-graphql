"""Test objects used to test the behavior of the api.

Usage: test_app.py

Attributes:
    TEST_DATABASE_URL: A str representing the location of the db used for
        testing

Classes:
    BasicAuthTestCase()
"""

import base64
import unittest
from unittest.mock import Mock

from graphql import GraphQLError
from werkzeug.security import generate_password_hash

from app import app
from auth import basic_auth
from models import User, setup_db

TEST_DATABASE_URL = "sqlite:///test_db.sqlite3"


class BasicAuthTestCase(unittest.TestCase):
    """Contains the test cases for testing user authentication.

    Attributes:
        app: A flask app from app.py
        mock: A mock object representing the fcn to be decorated by the
            basic_auth decorator
        basic_auth: A decorator used on the supplied mock object
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for the BasicAuthTestCase."""
        self.app = app
        app.config["DEBUG"] = False
        self.mock = Mock(return_value=True)
        self.basic_auth = basic_auth(self.mock)
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)
        user = User.query.filter_by(username="secureworks")
        if user is None:
            user = User(
                username="secureworks",
                password_hash=generate_password_hash("supersecret"),
            )
            user.insert()

    def test_basic_auth_success(self):
        """Test successful authentication when correct header is supplied."""
        auth = base64.b64encode(b"secureworks:supersecret").decode("utf-8")
        headers = {"Authorization": f"Basic {auth}"}
        with self.app.test_request_context(headers=headers):
            response = self.basic_auth()

        self.assertTrue(response)

    def test_basic_auth_no_auth_header_fail(self):
        """Test login failure when Authorization header is missing."""
        with self.app.test_request_context():
            self.assertRaises(GraphQLError, self.basic_auth)

    def test_basic_auth_invalid_auth_header_fail(self):
        """Test login failure when Auth header is not using basic auth."""
        auth = base64.b64encode(b"secureworks:supersecret").decode("utf-8")
        headers = {"Authorization": auth}
        with self.app.test_request_context(headers=headers):
            self.assertRaises(GraphQLError, self.basic_auth)

    def test_basic_auth_cant_decode_auth_header_fail(self):
        """Test login failure when Auth header is not base64 encoded."""
        headers = {"Authorization": "Basic secureworks:supersecret"}
        with self.app.test_request_context(headers=headers):
            self.assertRaises(GraphQLError, self.basic_auth)

    def test_basic_auth_missing_password_fail(self):
        """Test login failure when password is missing."""
        auth = base64.b64encode(b"secureworks").decode("utf-8")
        headers = {"Authorization": f"Basic {auth}"}
        with self.app.test_request_context(headers=headers):
            self.assertRaises(GraphQLError, self.basic_auth)

    def test_basic_auth_invalid_user_fail(self):
        """Test login failure when invalid user is supplied."""
        auth = base64.b64encode(b"insecureworks:supersecret").decode("utf-8")
        headers = {"Authorization": f"Basic {auth}"}
        with self.app.test_request_context(headers=headers):
            self.assertRaises(GraphQLError, self.basic_auth)

    def test_basic_auth_invalid_password_fail(self):
        """Test login failure when invalid password is supplied."""
        auth = base64.b64encode(b"secureworks:password").decode("utf-8")
        headers = {"Authorization": f"Basic {auth}"}
        with self.app.test_request_context(headers=headers):
            self.assertRaises(GraphQLError, self.basic_auth)


if __name__ == "__main__":
    unittest.main()
