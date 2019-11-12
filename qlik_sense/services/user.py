"""
This module provides the mechanics for interacting with Qlik Sense users. It uses a one-to-one model
to wrap the QRS endpoints and uses marshmallow to parse the results into Qlik Sense Stream objects where appropriate.
"""
from typing import TYPE_CHECKING, List, Optional, Union
from dataclasses import asdict

from qlik_sense.models.user import UserCondensedSchema, UserSchema
from qlik_sense.services import util, base

if TYPE_CHECKING:
    from qlik_sense.clients.base import Client
    from qlik_sense.models.user import UserCondensed, User
    import requests


class UserService(base.BaseService):
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
        self.url = '/qrs/user'

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
        else:
            schema = UserCondensedSchema()
        return self._query(schema=schema, filter_by=filter_by, order_by=order_by, privileges=privileges,
                           full_attribution=full_attribution)

    def get_by_name_and_directory(self, user_name: str, directory: str,
                                  full_attribution: bool = False) -> 'Optional[Union[UserCondensed, User]]':
        """
        This method is such a common use case of the query() method that it gets its own method

        Args:
            user_name: name of the user, the is the AD username when the user is an AD user
            directory: Qlik directory of the user, this is the AD domain when the user is an AD user
            full_attribution: allows the response to contain the full user attribution,
            defaults to False (limited attribution)

        Returns: the Qlik Sense condensed User(s) that fit the criteria
        """
        filter_by = f"userId eq '{user_name}' and userDirectory eq '{directory}'"
        users = self.query(filter_by=filter_by, full_attribution=full_attribution)
        if isinstance(users, list) and len(users) > 0:
            return users[0]
        return

    def get(self, id: str, privileges: 'Optional[List[str]]' = None) -> 'Optional[User]':
        """
        This method returns a Qlik Sense stream by its id

        Args:
            id: id of the stream on the server in uuid format
            privileges:

        Returns: a Qlik Sense User with full attribution
        """
        return self._get(schema=UserSchema(), id=id, privileges=privileges)

    def get_template(self, list_entries: bool = False) -> 'Optional[User]':
        """
        Gets a user, initialized with default values.
        Optionally, select if the objects that are referenced by the user are to be initialized
        by default or set to null.

        Args:
            list_entries: if true, turns this into a recursive call, returns default objects for all nested objects

        Returns: a default user
        """
        return self._get_template(schema=UserSchema(), entity_type='user', list_entries=list_entries)

    def get_new_id(self) -> str:
        """
        Gets a new user id, so that a new user can be generated. This happens automatically in create() if the supplied
        new user does not have an id, but is exposed here for convenience.

        Returns: a new user id as a uuid
        """
        user = self.get_template(list_entries=False)
        return user.id

    def create(self, user: 'User', privileges: 'Optional[List[str]]' = None) -> 'Optional[User]':
        """
        This method creates a new user on the server with the provided attribution

        Args:
            user: the new user
            privileges:
        """
        if user.id is None:
            user.id = self.get_new_id()
        return self._create(schema=UserSchema(), entity=user, privileges=privileges)

    def create_many(self, users: 'List[User]', privileges: 'Optional[List[str]]' = None) -> 'Optional[List[User]]':
        """
        This method creates new users on the server with the provided attribution

        Args:
            users: a list of new users
            privileges:
        """
        for user in users:
            if user.id is None:
                user.id = self.get_new_id()
        return self._create_many(schema=UserSchema(), entities=users, privileges=privileges)

    def update(self, user: 'User', privileges: 'Optional[List[str]]' = None) -> 'Optional[User]':
        """
        This method updates attributes of the provided user on the server

        Args:
            user: user to update
            privileges:
        """
        return self._update(schema=UserSchema(), entity=user, privileges=privileges)

    def delete(self, user: 'UserCondensed'):
        """
        This method deletes the provided user from the server

        Args:
            user: user to delete
        """
        self._delete(entity=user)
