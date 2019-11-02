"""
This module provides the mechanics for interacting with Qlik Sense apps. It uses a one-to-one model
to wrap the QRS endpoints and uses marshmallow to parse the results into Qlik Sense App objects where appropriate.
"""
from typing import TYPE_CHECKING, List, Optional, Iterable
from dataclasses import asdict

import uuid

from qlik_sense.models import app, stream
from qlik_sense.services import util

if TYPE_CHECKING:
    from qlik_sense.client import Client
    import requests


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
        self.schema = app.AppSchema()
        self.schema_condensed = app.AppCondensedSchema()
        self.url = '/qrs/app'

    def _call(self, request: 'util.QSAPIRequest') -> 'requests.Response':
        return self.client.call(**asdict(request))

    def query(self, filter_by: str = None, order_by: str = None,
              privileges: 'Optional[List[str]]' = None) -> 'Optional[List[app.AppCondensed]]':
        """
        This method queries Qlik Sense apps based on the provided criteria

        Args:
            filter_by: a filter string in jquery format
            order_by: an order by string
            privileges:

        Returns: a list of Qlik Sense Apps that meet the query_string criteria (or None)
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

    def get_by_name_and_stream(self, app_name: str, stream_name: str) -> 'Optional[List[app.AppCondensed]]':
        """
        This method is such a common use case of the query() method that it gets its own method

        Args:
            app_name: name of the app
            stream_name: name of the stream

        Returns: the Qlik Sense app(s) that fit the criteria
        """
        filter_by = f"name eq '{app_name}' and stream.name eq '{stream_name}'"
        return self.query(filter_by=filter_by)

    def get(self, id: str, privileges: 'Optional[List[str]]' = None) -> 'Optional[app.App]':
        """
        This method returns a Qlik Sense app by its id

        Args:
            id: id of the app on the server in uuid format
            privileges:

        Returns: a Qlik Sense app
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

    def update(self, app: 'app.App', privileges: 'Optional[List[str]]' = None):
        """
        This method updates attributes of the provided app on the server

        Args:
            app: app to update
            privileges:
        """
        request = util.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{app.id}',
            params={'privileges': privileges},
            data=asdict(app)
        )
        self._call(request)

    def delete(self, app: 'app.AppCondensed'):
        """
        This method deletes the provided app from the server

        Args:
            app: app to delete
        """
        request = util.QSAPIRequest(
            method='DELETE',
            url=f'{self.url}/{app.id}'
        )
        self._call(request)

    def reload(self, app: 'app.AppCondensed'):
        """
        This method reloads the provided app

        Args:
            app: app to reload
        """
        request = util.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/reload'
        )
        self._call(request)

    def copy(self, app: 'app.AppCondensed', name: str = None):
        """
        This method copies the provided app

        Args:
            app: app to copy
            name: name for the new app
        """
        request = util.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/copy',
            params={'name': name} if name else None
        )
        self._call(request)

    def export(self, app: 'app.AppCondensed', keep_data: bool = False) -> 'Optional[str]':
        """
        This method returns a download path for the provided app. It can be passed into download_file() to obtain
        the app itself

        Args:
            app: app to export
            keep_data: indicates if the data should be exported with the app

        Returns: the download path extension for the app (i.e. localhost/qrs/app/{returns this piece})
        """
        token = uuid.uuid4()
        request = util.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/export/{token}',
            params={'skipdata': not keep_data}
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return response.json()['downloadPath']
        return None

    def unpublish(self, app: 'app.AppCondensed'):
        """
        Unpublishes the provided app

        Args:
            app: app to unpublish
        """
        request = util.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/unpublish'
        )
        self._call(request)

    def delete_export(self, app: 'app.AppCondensed', token: 'uuid.UUID'):
        """
        This method cancels the download path for the provided app.

        Args:
            app: app originally getting exported
            token: download token
        """
        request = util.QSAPIRequest(
            method='DELETE',
            url=f'{self.url}/{app.id}/export/{token}'
        )
        self._call(request)

    def publish(self, app: 'app.AppCondensed', stream: 'stream.StreamCondensed', name: str = None):
        """
        This method will publish the provided app to the provided stream

        Args:
            app: app to publish
            stream: stream to which to publish the app
            name: name of the published app
        """
        request = util.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{app.id}/publish',
            params={'stream': stream.id, 'name': name if name else app.name}
        )
        self._call(request)

    def replace(self, app: 'app.AppCondensed', app_to_replace: 'app.AppCondensed'):
        """
        This method replaces the target app with the provided app

        Args:
            app: app to copy
            app_to_replace: app to replace
        """
        request = util.QSAPIRequest(
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
        request = util.QSAPIRequest(
            method='GET',
            url=f'{self.url}/{url}'
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return response.iter_content(chunk_size=512 << 10)
        return None
