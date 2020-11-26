"""A Flask-based api implemented with GraphQL and basic authentication.

Usage: flask run

Attributes:
    app: A flask Flask object creating the flask app
"""
from flask import Flask
from schema import schema

from auth import AuthGraphQLView
from models import setup_db

app = Flask(__name__)
setup_db(app)


app.add_url_rule(
    "/graphql",
    view_func=AuthGraphQLView.as_view("graphql", schema=schema, graphiql=True),
)


if __name__ == "__main__":
    app.run(debug=True)
