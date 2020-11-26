"""Model objects used to model data for the db.

Attributes:
    DATABASE_URL: A str representing the location of the db
    db: A SQLAlchemy service
    ip_details_response_codes: A SQLAlchemy association table to map the
        many-to-many relationship between ip details and response codes

Classes:
    User()
    IPDetails()
    ResponseCode()
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
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


ip_details_response_codes = db.Table(
    "ip_details_response_codes",
    Column(
        "ip_details_uuid",
        Integer,
        ForeignKey("ip_details.uuid"),
        primary_key=True,
    ),
    Column(
        "response_code_uuid",
        Integer,
        ForeignKey("response_codes.uuid"),
        primary_key=True,
    ),
)


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


class IPDetails(db.Model):
    """A model representing details of an IP address.

    Attributes:
        uuid: An int representing the unique identifier for the IP address
        created_at: A datetime representing when the obj was created
        updated_at: A datetime representing when the obj was last updated
        response_codes: A list of ResponseCode objects representing the
            response codes received from the last blocklist query
        ip_address: A str representing the ip address of the obj
    """

    __tablename__ = "ip_details"

    uuid = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=False)
    response_codes = relationship(
        "ResponseCode",
        secondary=ip_details_response_codes,
        backref="ip_details",
    )
    ip_address = Column(String, unique=True, nullable=False)

    def insert(self):
        """Inserts a new ip details object into the db."""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Updates an existing ip details object in the db."""
        self.updated_at = func.now()
        db.session.commit()


class ResponseCode(db.Model):
    """A model representing a response code from a blocklist query.

    Attributes:
        uuid: An int representing the unique identifier for the response code
        response_code: A str representing the returned response code from a
            blocklist query
    """

    __tablename__ = "response_codes"

    uuid = Column(Integer, primary_key=True)
    response_code = Column(String, unique=True, nullable=False)

    def insert(self):
        """Inserts a new response code object into the db."""
        db.session.add(self)
        db.session.commit()
