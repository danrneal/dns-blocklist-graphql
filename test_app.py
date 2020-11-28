"""Test objects used to test the behavior of the api.

Usage: test_app.py

Attributes:
    TEST_DATABASE_URL: A str representing the location of the db used for
        testing

Classes:
    BasicAuthTestCase()
    DNSLookupTestCase()
    GraphQLTestCase()
"""

import base64
import time
import unittest
from unittest.mock import Mock

from graphene.test import Client
from graphql import GraphQLError
from werkzeug.security import generate_password_hash

from app import app
from auth import basic_auth
from dns_lookup import dns_lookup, upsert_ip_details
from models import IPDetails, User, db, setup_db
from schema import Enqueue, Query, schema

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


class DNSLookupTestCase(unittest.TestCase):
    """Contains the test cases for testing DNS lookup background job.

    Attributes:
        app: A flask app from app.py
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for the DNSLookupTestCase."""
        self.app = app
        app.config["DEBUG"] = False
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def test_dns_lookup_no_response_code_success(self):
        """Test successful DNS lookup when no response codes are expected."""
        response_codes = dns_lookup("127.0.0.1")
        self.assertEqual(len(response_codes), 0)

    def test_dns_lookup_response_code_success(self):
        """Test successful DNS lookup when response code(s) are expected."""
        response_codes = dns_lookup("127.0.0.2")
        self.assertGreater(len(response_codes), 0)

    def test_dns_lookup_incomplete_ip_address_fail(self):
        """Test DNS lookup failure when ip address is incomplete."""
        self.assertRaises(TypeError, dns_lookup, "127.0.0")

    def test_dns_lookup_malformed_ip_address_fail(self):
        """Test DNS lookup failure when ip address is malformed."""
        self.assertRaises(TypeError, dns_lookup, "127.0.0.A")

    def test_upsert_ip_details_insert_success(self):
        """Test successful insert into the db after DNS lookup."""
        ip_details = IPDetails.query.filter_by(ip_address="127.0.0.1").first()
        if ip_details is not None:
            db.session.delete(ip_details)
            db.session.commit()

        upsert_ip_details("127.0.0.1")
        ip_details = IPDetails.query.filter_by(ip_address="127.0.0.1").first()
        self.assertIsNotNone(ip_details)
        self.assertEqual(ip_details.created_at, ip_details.updated_at)

    def test_upsert_up_details_update_success(self):
        """Test successful update into the db after DNS lookup."""
        ip_details = IPDetails.query.filter_by(ip_address="127.0.0.2").first()
        if ip_details is not None:
            db.session.delete(ip_details)
            db.session.commit()

        ip_details = IPDetails(ip_address="127.0.0.2")
        ip_details.insert()
        time.sleep(1)
        upsert_ip_details("127.0.0.2")
        ip_details = IPDetails.query.filter_by(ip_address="127.0.0.2").first()
        self.assertIsNotNone(ip_details)
        self.assertGreater(ip_details.updated_at, ip_details.created_at)


class GraphQLTestCase(unittest.TestCase):
    """Contains the test cases for testing the graphql endpoint.

    Attributes:
        app: A flask app from app.py
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for the GraphQLTestCase."""
        self.app = app
        app.config["DEBUG"] = False
        self.client = Client(schema)
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def test_enqueue_success(self):
        """Test successful enqueue."""
        ip_addresses = ["127.0.0.1", "127.0.0.2"]
        enqueue = Enqueue()
        result = enqueue.mutate(None, ip_addresses)
        self.assertEqual(result.ip_addresses, ip_addresses)

    def test_mutation_enqueue_success(self):
        """Test successful enqueue mutation request."""
        result = self.client.execute(
            """
            mutation {
                enqueue(ipAddresses: ["127.0.0.1", "127.0.0.2"]) {
                    ipAddresses
                }
            }
            """
        )
        self.assertIsNone(result.get("errors"))
        self.assertEqual(
            result["data"]["enqueue"]["ipAddresses"],
            ["127.0.0.1", "127.0.0.2"],
        )

    def test_query_resolve_get_ip_details_success(self):
        """Test successful resolution of get_ip_details."""
        ip_details = IPDetails.query.filter_by(ip_address="127.0.0.1").first()
        if ip_details is None:
            ip_details = IPDetails(ip_address="127.0.0.1")
            ip_details.insert()

        query = Query()
        result = query.resolve_get_ip_details(None, "127.0.0.1")
        self.assertEqual(result, ip_details)

    def test_query_resolve_get_ip_details_not_found_fail(self):
        """Test failed resolution of get_ip_details if ip address not found."""
        ip_details = IPDetails.query.filter_by(ip_address="127.0.0.3").first()
        if ip_details is not None:
            db.session.delete(ip_details)
            db.session.commit()

        query = Query()
        self.assertRaises(
            GraphQLError, query.resolve_get_ip_details, None, "127.0.0.3",
        )

    def test_query_get_ip_details_success(self):
        """Test successful get_ip_details query request."""
        ip_details = IPDetails.query.filter_by(ip_address="127.0.0.1").first()
        if ip_details is None:
            ip_details = IPDetails(ip_address="127.0.0.1")
            ip_details.insert()

        result = self.client.execute(
            """
            query {
                getIpDetails(ipAddress: "127.0.0.1"){
                    uuid
                    createdAt
                    updatedAt
                    ipAddress
                    responseCodes {
                        responseCode
                    }
                }
            }
            """
        )
        self.assertIsNone(result.get("errors"))
        self.assertIsNotNone(result["data"]["getIpDetails"].get("uuid"))
        self.assertIsNotNone(result["data"]["getIpDetails"].get("createdAt"))
        self.assertIsNotNone(result["data"]["getIpDetails"].get("updatedAt"))
        self.assertIsNotNone(result["data"]["getIpDetails"].get("uuid"))
        self.assertIsNotNone(
            result["data"]["getIpDetails"].get("responseCodes")
        )
        self.assertEqual(
            result["data"]["getIpDetails"].get("ipAddress"), "127.0.0.1"
        )


if __name__ == "__main__":
    unittest.main()
