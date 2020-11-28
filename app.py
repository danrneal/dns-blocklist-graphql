"""A Flask-based api implemented with GraphQL and basic authentication.

Usage: flask run

Attributes:
    app: A flask Flask object creating the flask app
"""
import os

from flask import Flask

from auth import AuthGraphQLView
from models import setup_db
from schema import schema

app = Flask(__name__)
setup_db(app)


app.add_url_rule(
    "/graphql", view_func=AuthGraphQLView.as_view("graphql", schema=schema),
)


if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(port=port)
