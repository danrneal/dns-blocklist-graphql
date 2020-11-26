"""A Flask-based api implemented with GraphQL and basic authentication.

Usage: flask run

Attributes:
    app: A flask Flask object creating the flask app
"""
from flask import Flask

app = Flask(__name__)


if __name__ == "__main__":
    app.run(debug=True)
