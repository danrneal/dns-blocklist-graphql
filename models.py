"""Model objects used to model data for the db.

Attributes:
    DATABASE_URL: A str representing the location of the db
    db: A SQLAlchemy service

Classes:
    User()
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from werkzeug.security import check_password_hash

DATABASE_URL = "sqlite:///db.sqlite3"
db = SQLAlchemy()


def setup_db(app, database_url=DATABASE_URL):
    """Binds a flask application and a SQLAlchemy service.

    Args:
        app: A flask app
        database_url: A str representing the location of the db (default:
            global DATABASE_URL)
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class User(db.Model):
    """A model representing a user.

    Attributes:
        uuid: An int representing the unique identifier for the user
        username: A str representing the unique name for the user
        password_hash: A str representing the hashed password for the user
    """

    __tablename__ = "users"

    uuid = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def insert(self):
        """Inserts a new user object into the db."""
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        """Check if a given password is correct for this user."""
        return check_password_hash(self.password_hash, password)
