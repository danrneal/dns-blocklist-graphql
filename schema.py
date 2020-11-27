"""The GraphQL schema for the /graphql endpoint.

Attributes:
    schema: A graphene Schema object

Classes:
    IPDetailsType()
    Enqueue()
    Mutation()
"""

import concurrent.futures

import graphene
from graphene import Field, List, String
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError

from dns_lookup import upsert_ip_details
from models import IPDetails, ResponseCode


class IPDetailsType(SQLAlchemyObjectType):
    """Creates a SQLAlchemy object type for IPDetails model.

    Classes:
        Meta()
    """

    class Meta:
        """Sets the model for the SQLAlchemy Object Type."""

        model = IPDetails


class ResponseCodeType(SQLAlchemyObjectType):
    """Creates a SQLAlchemy object type for Response model.

    Classes:
        Meta()
    """

    class Meta:
        """Sets the model for the SQLAlchemy Object Type."""

        model = ResponseCode


class Enqueue(graphene.Mutation):
    """Create enqueue mutation for the graphql endpoint.

    Attributes:
        ip_addresses: A list of strs representing the ip addresses to perform
            the mutation on

    Classes:
        Arguments()
    """

    ip_addresses = List(String)

    class Arguments:
        """Sets the arguments allowed for this mutation.

        Attributes:
            ip_addresses: A list of strs representing the ip addresses passed
                in as an arg to the mutation
        """

        ip_addresses = List(String)

    def mutate(self, _, ip_addresses):  # pylint: disable=no-self-use
        """Allow for mutation logic in this mutation.

        Args:
            ip_addresses: A list of strs representing the ip addresses to
                enqueue to the upsert func

        Returns:
            An enqueue mutation object with the passed in ip addresses set as
                an attribute
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(upsert_ip_details, ip_addresses)

        return Enqueue(ip_addresses=ip_addresses)


class Query(graphene.ObjectType):
    """Create queries allowed at the graphql endpoint.

    Attributes:
        get_ip_details: An IPDetailsType object representing the IPDetails
            model for the query
        response_code: A list of ResponseCodeTypes representing the
            ResponseCode model for the query
    """

    get_ip_details = Field(IPDetailsType, ip_address=String(required=True))
    response_code = List(ResponseCodeType)

    def resolve_get_ip_details(
        self, _, ip_address
    ):  # pylint: disable=no-self-use
        """The resolver method for get_ip_details for the query.

        Args:
            ip_address: A str presenting the ip address to lookup in the db

        Returns:
            ip_details: An IPDetails object representing the details for the
                given ip address
        """
        ip_details = IPDetails.query.filter_by(ip_address=ip_address).first()
        if ip_details is None:
            raise GraphQLError("Details for given IP address cannot be found")

        return ip_details


class Mutation(graphene.ObjectType):
    """Create mutations allowed at the graphql endpoint.

    Attributes:
        enqueue: A graphene Mutation object representing an allowed mutation at
            the graphql endpoint
    """

    enqueue = Enqueue.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
