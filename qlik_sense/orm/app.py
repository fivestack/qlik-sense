"""
This module provides the mechanics for directly interacting with Qlik Sense apps. It uses a one-to-one model
to wrap the QRS endpoints and uses marshmallow to parse the results into qlik_sense App objects.
"""
from typing import TYPE_CHECKING, List

import uuid
import marshmallow as ma

if TYPE_CHECKING:
    from qlik_sense.orm.controller import Controller
    from qlik_sense import models


class AppSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a qlik_sense App object
    """
    guid = ma.fields.Str(required=True, data_key='id')
    name = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'models.App':
        return models.App(**data)


class AppSession:
    """
    AppSession wraps each one of the app-based QlikSense endpoints in a method. This buffers the application
    from API updates. It also allows for the Session class to be mocked for tests instead of the entire QRS API (or
    Controller class).

    Args:
        controller: a Controller class that provides an interface over the QRS API
    """

    def __init__(self, controller: 'Controller'):
        self.controller = controller
        self.schema = AppSchema()
        self.url = '/qrs/app'

    def query(self, query_string: str) -> 'List[models.App]':
        response = self.controller.get(url=self.url, params={'filter': query_string}).json()
        return self.schema.loads(response)

    def query_one(self, guid: str) -> 'models.App':
        app = self.controller.get(url=f'{self.url}/{guid}').json()
        return self.schema.loads(app)

    def update(self, app: 'models.App', updates: dict):
        self.controller.put(url=f'{self.url}/{app.guid}', data=updates)

    def delete(self, app: 'models.App'):
        self.controller.delete(url=f'{self.url}/{app.guid}')

    def reload(self, app: 'models.App'):
        self.controller.post(url=f'{self.url}/{app.guid}/reload')

    def copy(self, app: 'models.App', name: str = None):
        params = {'name': name} if name else None
        self.controller.post(url=f'{self.url}/{app.guid}/copy', params=params)

    def export(self, app: 'models.App') -> str:
        token = uuid.uuid4()
        response = self.controller.post(url=f'{self.url}/{app.guid}/export/{token}')
        return response.json()['downloadPath']

    def publish(self, app: 'models.App', stream: 'models.Stream'):
        self.controller.put(url=f'{self.url}/{app.guid}/publish', params={'stream': stream.guid})

    def replace(self, app: 'models.App', app_to_replace: 'models.App'):
        self.controller.put(url=f'{self.url}/{app.guid}/replace', params={'app': app_to_replace.guid})

    def upload(self, file, params: dict):
        self.controller.post(url=f'{self.url}/upload', params=params, data=file)

    def download_file(self, url: str) -> iter:
        return self.controller.get(url=url).iter_content(chunk_size=512 << 10)
