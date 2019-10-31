"""
This module provides the mechanics for interacting with Qlik Sense apps. It uses a one-to-one model
to wrap the QRS endpoints and uses marshmallow to parse the results into Qlik Sense App objects where appropriate.
"""
from typing import TYPE_CHECKING, List, Optional, Iterable
from dataclasses import asdict

import uuid
import marshmallow as ma

from qlik_sense import models

if TYPE_CHECKING:
    from qlik_sense.client import Client
    import requests


class _StreamSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense Schema object
    """
    id = ma.fields.Str(required=True)
    name = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'models.Stream':
        return models.Stream(**data)


class _AppSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense App object
    """
    id = ma.fields.Str(required=True)
    name = ma.fields.Str(required=False)
    stream = ma.fields.Nested(_StreamSchema, required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'models.App':
        return models.App(**data)


class AppService:
    """
    AppService wraps each one of the app-based QlikSense endpoints in a method. This buffers the application
    from API updates.

    Args:
        client: a Client class that provides an interface over the Qlik Sense APIs
    """
    requests = list()

    def __init__(self, client: 'Client'):
        self.client = client
        self.schema = _AppSchema()
        self.url = '/qrs/app'

    def _call(self, request: 'models.QSAPIRequest') -> 'requests.Response':
        return self.client.call(**asdict(request))

    def query(self, query_string: str) -> 'Optional[List[models.App]]':
        """
        This method queries Qlik Sense apps based on the provided criteria

        Args:
            query_string: a filter string in jquery? format

        Returns: a list of Qlik Sense Apps that meet the query_string criteria (or None)
        """
        request = models.QSAPIRequest(
            method='GET',
            url=f'{self.url}',
            params={'filter': query_string}
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return self.schema.loads(response.json())
        return None

    def get_by_name_and_stream(self, app_name: str, stream_name: str) -> 'Optional[List[models.App]]':
        """
        This method is such a common use case of the query() method that it gets its own method

        Args:
            app_name: name of the app
            stream_name: name of the stream

        Returns: the Qlik Sense app(s) that fit the criteria
        """
        query_string = f"name eq '{app_name}' and stream.name eq '{stream_name}'"
        return self.query(query_string=query_string)

    def get(self, id: str) -> 'Optional[models.App]':
        """
        This method returns a Qlik Sense app by its id

        Args:
            id: id of the app on the server in uuid format

        Returns: a Qlik Sense app
        """
        request = models.QSAPIRequest(
            method='GET',
            url=f'{self.url}/{id}'
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return self.schema.loads(response.json())
        return None

    def update(self, app: 'models.App'):
        """
        This method updates attributes of the provided app on the server

        Args:
            app: app to update
        """
        request = models.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{app.id}'
        )
        self._call(request)

    def delete(self, app: 'models.App'):
        """
        This method deletes the provided app from the server

        Args:
            app: app to delete
        """
        request = models.QSAPIRequest(
            method='DELETE',
            url=f'{self.url}/{app.id}'
        )
        self._call(request)

    def reload(self, app: 'models.App'):
        """
        This method reloads the provided app

        Args:
            app: app to reload
        """
        request = models.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/reload'
        )
        self._call(request)

    def copy(self, app: 'models.App', name: str = None):
        """
        This method copies the provided app

        Args:
            app: app to copy
            name: name for the new app
        """
        request = models.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/copy',
            params={'name': name} if name else None
        )
        self._call(request)

    def export(self, app: 'models.App') -> 'Optional[str]':
        """
        This method returns a download path for the provided app. It can be passed into download_file() to obtain
        the app itself

        Args:
            app: app to export

        Returns: the download path extension for the app (i.e. localhost/qrs/app/{returns this piece})
        """
        token = uuid.uuid4()
        request = models.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/export/{token}'
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return response.json()['downloadPath']
        return None

    def publish(self, app: 'models.App', stream: 'models.Stream'):
        """
        This method will publish the provided app to the provided stream

        Args:
            app: app to publish
            stream: stream to which to publish the app
        """
        request = models.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{app.id}/publish',
            params={'stream': stream.id}
        )
        self._call(request)

    def replace(self, app: 'models.App', app_to_replace: 'models.App'):
        """
        This method replaces the target app with the provided app

        Args:
            app: app to copy
            app_to_replace: app to replace
        """
        request = models.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{app.id}/replace',
            params={'app': app_to_replace.id}
        )
        self._call(request)

    def download_file(self, url: str) -> 'Optional[Iterable]':
        """
        This method downloads an app given a download link

        Args:
            url: download path extension for the app (i.e., localhost/qrs/app/{this piece}
        """
        request = models.QSAPIRequest(
            method='GET',
            url=f'{self.url}/{url}'
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return response.iter_content(chunk_size=512 << 10)
        return None
