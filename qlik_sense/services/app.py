"""
This module provides the mechanics for directly interacting with Qlik Sense apps. It uses a one-to-one model
to wrap the QRS endpoints and uses marshmallow to parse the results into qlik_sense App objects.
"""
from typing import TYPE_CHECKING, List, Optional, Iterable
from dataclasses import asdict
import json

import uuid
import marshmallow as ma

from qlik_sense import models

if TYPE_CHECKING:
    from qlik_sense.client import Client
    import requests


class StreamSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a qlik_sense Schema object
    """
    id = ma.fields.Str(required=True)
    name = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'models.Stream':
        return models.Stream(**data)


class AppSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a qlik_sense App object
    """
    id = ma.fields.Str(required=True)
    name = ma.fields.Str(required=False)
    stream = ma.fields.Nested(StreamSchema, required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'models.App':
        return models.App(**data)


class AppService:
    """
    AppSession wraps each one of the app-based QlikSense endpoints in a method. This buffers the application
    from API updates. It also allows for the Session class to be mocked for tests instead of the entire QRS API (or
    Controller class).

    Args:
        client: a Controller class that provides an interface over the QRS API
    """
    requests = None

    def __init__(self, client: 'Client'):
        self.client = client
        self.schema = AppSchema()
        self.url = '/qrs/app'

    def _call(self, request: 'models.QSAPIRequest') -> 'requests.Response':
        if request.data:
            if isinstance(request.data, dict) or isinstance(request.data, list):
                request.data = json.dumps(request.data)
        return self.client.call(**asdict(request))

    def query(self, query_string: str) -> 'Optional[List[models.App]]':
        request = models.QSAPIRequest(
            method='GET',
            url=f'{self.url}',
            params={'filter': query_string}
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return self.schema.loads(response.json())
        return None

    def query_one(self, id: str) -> 'Optional[models.App]':
        request = models.QSAPIRequest(
            method='GET',
            url=f'{self.url}/{id}'
        )
        response = self._call(request)
        if 200 <= response.status_code < 300:
            return self.schema.loads(response.json())
        return None

    def update(self, app: 'models.App'):
        request = models.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{app.id}'
        )
        self._call(request)

    def delete(self, app: 'models.App'):
        request = models.QSAPIRequest(
            method='DELETE',
            url=f'{self.url}/{app.id}'
        )
        self._call(request)

    def reload(self, app: 'models.App'):
        request = models.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/reload'
        )
        self._call(request)

    def copy(self, app: 'models.App', name: str = None):
        request = models.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/copy',
            params={'name': name} if name else None
        )
        self._call(request)

    def export(self, app: 'models.App') -> str:
        token = uuid.uuid4()
        request = models.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/export/{token}'
        )
        response = self._call(request)
        return response.json()['downloadPath']

    def publish(self, app: 'models.App', stream: 'models.Stream'):
        request = models.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{app.id}/publish',
            params={'stream': stream.id}
        )
        self._call(request)

    def replace(self, app: 'models.App', app_to_replace: 'models.App'):
        request = models.QSAPIRequest(
            method='PUT',
            url=f'{self.url}/{app.id}/replace',
            params={'app': app_to_replace.id}
        )
        self._call(request)

    def upload(self, file, params: dict):
        request = models.QSAPIRequest(
            method='POST',
            url=f'{self.url}/upload',
            params=params,
            data=file
        )
        self._call(request)

    def download_file(self, url: str) -> Iterable:
        request = models.QSAPIRequest(
            method='GET',
            url=url
        )
        response = self._call(request)
        return response.iter_content(chunk_size=512 << 10)
