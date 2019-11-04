"""
This module provides the mechanics for interacting with Qlik Sense users. It uses a one-to-one model
to wrap the QRS endpoints and uses marshmallow to parse the results into Qlik Sense Stream objects where appropriate.
"""
from typing import TYPE_CHECKING, List, Optional, Union
from dataclasses import asdict

from qlik_sense.models.user import UserCondensedSchema, UserSchema
from qlik_sense.services import util

if TYPE_CHECKING:
    from qlik_sense.clients.base import Client
    from qlik_sense.models.user import UserCondensed, User
    import requests


class UserService:
    """
    UserService wraps each one of the user-based QlikSense endpoints in a method. This buffers the application
    from API updates.

    Args:
        client: a Client class that provides an interface over the Qlik Sense APIs

    Supported Methods:

        - qrs/user: GET, POST
        - qrs/user/many: POST
        - qrs/user/count: GET
        - qrs/user/full: GET
        - qrs/user/{user.id}: GET, PUT, DELETE

    Unsupported Methods:

        - qrs/user/ownedresources: GET
        - qrs/user/sync/{userdirectory}/{user.id}: GET
        - qrs/user/previewcreateprivilege: POST
        - qrs/user/previewprivileges: POST
        - qrs/user/table: POST
    """
    requests = list()

    def __init__(self, client: 'Client'):
        self.client = client
        self.url = '/qrs/stream'

    def _call(self, request: 'util.QSAPIRequest') -> 'requests.Response':
        return self.client.call(**asdict(request))

    def query(self, filter_by: str = None, order_by: str = None, privileges: 'Optional[List[str]]' = None,
              full_attribution: bool = False) -> 'Optional[List[Union[UserCondensed, User]]]':
        """
        This method queries Qlik Sense users based on the provided criteria and provides either partial or
        full attribution of the users based on the setting of full_attribution

        Args:
            filter_by: a filter string in jquery format
            order_by: an order by string
            privileges:
            full_attribution: allows the response to contain the full user attribution,
            defaults to False (limited attribution)

        Returns: a list of Qlik Sense Users that meet the query_string criteria (or None)
        """
        if full_attribution:
            schema = UserSchema()
            url = f'{self.url}/full'
        else:
            schema = UserCondensedSchema()
            url = f'{self.url}'
        params = {
            'filter': filter_by,
            'orderby': order_by,
            'privileges': privileges
        }
        request = util.QSAPIRequest(method='GET', url=url, params=params)
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.json(), many=True)
        return None

    def query_count(self, filter_by: str = None) -> 'Optional[int]':
        """
        This method queries Qlik Sense users based on the provided criteria and returns the count

        Args:
            filter_by: a filter string in jquery format

        Returns: the number of Qlik Sense Users that meet the query_string criteria (or None)
        """
        params = {'filter': filter_by}
        request = util.QSAPIRequest(method='GET', url=f'{self.url}/count', params=params)
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return int(response.text())
        return None

    def get_by_name(self, name: str) -> 'Optional[List[UserCondensed]]':
        """
        This method is such a common use case of the query() method that it gets its own method

        Args:
            name: name of the user

        Returns: the Qlik Sense condensed User(s) that fit the criteria
        """
        filter_by = f"name eq '{name}'"
        return self.query(filter_by=filter_by)

    def get(self, id: str, privileges: 'Optional[List[str]]' = None) -> 'Optional[User]':
        """
        This method returns a Qlik Sense stream by its id

        Args:
            id: id of the stream on the server in uuid format
            privileges:

        Returns: a Qlik Sense User with full attribution
        """
        schema = UserSchema()
        request = util.QSAPIRequest(
            method='GET',
            url=f'{self.url}/{id}',
            params={'privileges': privileges}
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.json())
        return None

    def create(self, user: 'User', privileges: 'Optional[List[str]]' = None) -> 'Optional[User]':
        """
        This method creates a new user on the server with the provided attribution

        Args:
            user: the new user
            privileges:
        """
        schema = UserSchema()
        request = util.QSAPIRequest(
            method='POST',
            url=f'{self.url}',
            params={'privileges': privileges},
            data=asdict(user)
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.json())
        return None

    def create_many(self, users: 'List[User]', privileges: 'Optional[List[str]]' = None) -> 'Optional[List[User]]':
        """
        This method creates new users on the server with the provided attribution

        Args:
            users: a list of new users
            privileges:
        """
        schema = UserSchema()
        request = util.QSAPIRequest(
            method='POST',
            url=f'{self.url}/many',
            params={'privileges': privileges},
            data=[asdict(user) for user in users]
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.json(), many=True)
        return None

    def update(self, user: 'User', privileges: 'Optional[List[str]]' = None) -> 'Optional[User]':
        """
        This method updates attributes of the provided user on the server

        Args:
            user: user to update
            privileges:
        """
        schema = UserSchema()
        request = util.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{user.id}',
            params={'privileges': privileges},
            data=asdict(user)
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.json())
        return None

    def delete(self, user: 'UserCondensed'):
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
