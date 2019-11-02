"""
This module provides the mechanics for interacting with Qlik Sense users. It uses a one-to-one model
to wrap the QRS endpoints and uses marshmallow to parse the results into Qlik Sense Stream objects where appropriate.
"""
from typing import TYPE_CHECKING, List, Optional
from dataclasses import asdict

from qlik_sense.models import user
from qlik_sense.services import util

if TYPE_CHECKING:
    from qlik_sense.client import Client
    import requests


class UserService:
    """
    UserService wraps each one of the user-based QlikSense endpoints in a method. This buffers the application
    from API updates.

    Args:
        client: a Client class that provides an interface over the Qlik Sense APIs
    """
    requests = list()

    def __init__(self, client: 'Client'):
        self.client = client
        self.schema = user.UserSchema()
        self.schema_condensed = user.UserCondensedSchema()
        self.url = '/qrs/stream'

    def _call(self, request: 'util.QSAPIRequest') -> 'requests.Response':
        return self.client.call(**asdict(request))

    def query(self, filter_by: str = None, order_by: str = None,
              privileges: 'Optional[List[str]]' = None) -> 'Optional[List[user.UserCondensed]]':
        """
        This method queries Qlik Sense users based on the provided criteria

        Args:
            filter_by: a filter string in jquery format
            order_by: an order by string
            privileges:

        Returns: a list of Qlik Sense condensed Users that meet the query_string criteria (or None)
        """
        params = {
            'filter': filter_by,
            'orderby': order_by,
            'privileges': privileges
        }
        request = util.QSAPIRequest(
            method='GET',
            url=f'{self.url}',
            params=params
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return self.schema_condensed.loads(response.json())
        return None

    def get_by_name(self, name: str) -> 'Optional[List[user.UserCondensed]]':
        """
        This method is such a common use case of the query() method that it gets its own method

        Args:
            name: name of the user

        Returns: the Qlik Sense condensed User(s) that fit the criteria
        """
        filter_by = f"name eq '{name}'"
        return self.query(filter_by=filter_by)

    def get(self, id: str, privileges: 'Optional[List[str]]' = None) -> 'Optional[user.User]':
        """
        This method returns a Qlik Sense stream by its id

        Args:
            id: id of the stream on the server in uuid format
            privileges:

        Returns: a Qlik Sense Stream with full attribution
        """
        request = util.QSAPIRequest(
            method='GET',
            url=f'{self.url}/{id}',
            params={'privileges': privileges}
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return self.schema.loads(response.json())
        return None

    def create(self, new_user: user.User, privileges: 'Optional[List[str]]' = None):
        """
        This method creates a new user on the server with the provided attribution

        Args:
            new_user: the new user
            privileges:
        """
        request = util.QSAPIRequest(
            method='POST',
            url=f'{self.url}',
            params={'privileges': privileges},
            data=asdict(new_user)
        )
        self._call(request)

    def update(self, user: 'user.User', privileges: 'Optional[List[str]]' = None):
        """
        This method updates attributes of the provided user on the server

        Args:
            user: user to update
            privileges:
        """
        request = util.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{user.id}',
            params={'privileges': privileges},
            data=asdict(user)
        )
        self._call(request)

    def delete(self, user: 'user.UserCondensed'):
        """
        This method deletes the provided user from the server

        Args:
            user: user to delete
        """
        request = util.QSAPIRequest(
            method='DELETE',
            url=f'{self.url}/{user.id}'
        )
        self._call(request)