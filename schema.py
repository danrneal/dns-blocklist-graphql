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
from graphene import List, String
from graphene_sqlalchemy import SQLAlchemyObjectType

from dns_lookup import upsert_ip_details
from models import IPDetails


class IPDetailsType(SQLAlchemyObjectType):
    """Creates a SQLAlchemy object type for IPDetails model.

    Classes:
        Meta()
    """

    class Meta:
        """Sets the model for the SQLAlchemy Object Type."""

        model = IPDetails


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

        Arguments:
            ip_addresses: A list of strs representing the ip addresses to
                enqueue to the upsert func

        Returns:
            An enqueue mutation object with the passed in ip addresses set as
                an attribute
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(upsert_ip_details, ip_addresses)

        return Enqueue(ip_addresses=ip_addresses)


class Mutation(graphene.ObjectType):
    """Create mutations allowed at the graphql endpoint.

    Attributes:
        enqueue: A graphene Mutation object representing an allowed mutation at
            the graphql endpoint
    """

    enqueue = Enqueue.Field()


schema = graphene.Schema(mutation=Mutation)
