"""
This module provides a mixin with the base mechanics for interacting with Qlik Sense entities.
"""
import logging
import sys
from typing import TYPE_CHECKING, List, Optional, Union
from dataclasses import asdict
import abc
from datetime import datetime

from qlik_sense.models.base import EntityCondensedSchema, EntitySchema
from .util import QSAPIRequest

if TYPE_CHECKING:
    from qlik_sense.models.base import EntityCondensed, Entity
    import requests

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))
_logger.setLevel(logging.DEBUG)


class BaseService(abc.ABC):
    """
    BaseService wraps each one of the generic entity Qlik Sense endpoints in a method. This buffers the application
    from API updates and makes standing up/maintaining new entities easier and more consistent.

    Supported Methods:

        - qrs/<entity>: GET, POST
        - qrs/<entity>/many: POST
        - qrs/<entity>/count: GET
        - qrs/<entity>/full: GET
        - qrs/<entity>/{<entity>.id}: GET, PUT, DELETE
    """
    url = None
    client = None

    def _call(self, request: 'QSAPIRequest') -> 'requests.Response':
        return self.client.call(**asdict(request))

    def _query(self, schema: 'Union[EntityCondensedSchema, EntitySchema]',
               filter_by: str, order_by: str, privileges: 'Optional[List[str]]',
               full_attribution: bool) -> 'Optional[List[Union[EntityCondensed, Entity]]]':
        """
        This method queries Qlik Sense entities based on the provided criteria and provides either partial or
        full attribution of the entities based on the setting of full_attribution

        Args:
            schema: schema representing the object to return
            filter_by: a filter string in jquery format
            order_by: an order by string
            privileges:
            full_attribution: allows the response to contain either the full entity attribution, or a condensed version

        Returns: a list of Qlik Sense Entities that meet the query_string criteria (or None)
        """
        if full_attribution:
            url = f'{self.url}/full'
        else:
            url = self.url
        params = {
            'filter': filter_by,
            'orderby': order_by,
            'privileges': privileges
        }
        request = QSAPIRequest(method='GET', url=url, params=params)
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.content, many=True)
        return None

    def query_count(self, filter_by: str = None) -> 'Optional[int]':
        """
        This method queries Qlik Sense entities based on the provided criteria and returns the count

        Args:
            filter_by: a filter string in jquery format

        Returns: the number of Qlik Sense Entities that meet the query_string criteria (or None)
        """
        params = {'filter': filter_by}
        request = QSAPIRequest(method='GET', url=f'{self.url}/count', params=params)
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return int(response.json()['value'])
        return None

    def _get(self, schema: 'EntitySchema', id: str, privileges: 'Optional[List[str]]' = None) -> 'Optional[Entity]':
        """
        This method returns a Qlik Sense entity by its id

        Args:
            schema: schema representing the object to return
            id: id of the entity on the server in uuid format
            privileges:

        Returns: a Qlik Sense Entity with full attribution
        """
        request = QSAPIRequest(
            method='GET',
            url=f'{self.url}/{id}',
            params={'privileges': privileges}
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.content)
        return None

    def _get_template(self, schema: 'EntitySchema', entity_type: str, list_entries: bool = False) -> 'Optional[Entity]':
        """
        Gets an entity, initialized with default values, of a specific entity_type.
        Optionally, select if the objects that are referenced by the entities are to be initialized
        by default or set to null.

        Args:
            schema: schema to use to turn the json object into a python object, should correspond to entity_type
            entity_type: type of entity to return (e.g. user, stream, app, etc.)
            list_entries: if true, turns this into a recursive call, returns default objects for all nested objects

        Returns: a default entity
        """
        request = QSAPIRequest(
            method='GET',
            url=f'/qrs/about/api/default/{entity_type}',
            params={'listentries': list_entries}
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.content)
        return None

    def _create(self, schema: 'EntitySchema', entity: 'Entity',
                privileges: 'Optional[List[str]]' = None) -> 'Optional[Entity]':
        """
        This method creates a new entity on the server with the provided attribution

        Args:
            schema: schema representing the object to return
            entity: the new entity
            privileges:
        """
        entity.created_date = datetime.now()
        entity.modified_date = datetime.now()
        _logger.debug(f'__CREATE {entity}')
        request = QSAPIRequest(
            method='POST',
            url=f'{self.url}',
            params={'privileges': privileges},
            data=schema.dumps(entity)
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.content)
        return None

    def _create_many(self, schema: 'EntitySchema', entities: 'List[Entity]',
                     privileges: 'Optional[List[str]]' = None) -> 'Optional[List[Entity]]':
        """
        This method creates new entities on the server with the provided attribution

        Args:
            schema: schema representing the object to return
            entities: a list of new entities
            privileges:
        """
        for entity in entities:
            entity.created_date = datetime.now()
            entity.modified_date = datetime.now()
        request = QSAPIRequest(
            method='POST',
            url=f'{self.url}/many',
            params={'privileges': privileges},
            data=schema.dumps(entities, many=True)
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.content, many=True)
        return None

    def _update(self, schema: 'EntitySchema', entity: 'Entity',
                privileges: 'Optional[List[str]]' = None) -> 'Optional[Entity]':
        """
        This method updates attributes of the provided entity on the server

        Args:
            schema: schema representing the object to return
            entity: entity to update
            privileges:
        """
        request = QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{entity.id}',
            params={'privileges': privileges},
            data=schema.dumps(entity)
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return schema.loads(response.content)
        return None

    def _delete(self, entity: 'EntityCondensed'):
        """
        This method deletes the provided entity from the server

        Args:
            entity: entity to delete
        """
        request = QSAPIRequest(
            method='DELETE',
            url=f'{self.url}/{entity.id}'
        )
        self._call(request)
