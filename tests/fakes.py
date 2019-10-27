from typing import Union, TYPE_CHECKING, List
import json

import requests
import uuid

from .conftest import orm

if TYPE_CHECKING:
    from .conftest import models
    import requests


class FakeController(orm.Controller):
    """
    This is a fake controller that mocks out the actual API calls to the Qlik Sense server. All API calls are routed
    through _call() via the four HTTP method wrappers. Hence, _call() is overwritten with an empty function to ensure
    no actual API calls are made. And the four methods are overwritten to return mock Response objects, and more
    importantly, log the requests that are being made so that they can be inspected by the unit tests.
    """
    def __init__(self):
        user = {
            'directory': 'directory',
            'username': 'username',
            'password': 'password1234'
        }
        super().__init__(log_name='qlik_sense_test', verbosity='DEBUG',
                         schema='https', host='localhost', port=0,
                         certificate=None, user=user, verify=False)
        self.requests = list()

    def _call(self, method: str, url, params: dict = None, data: str = None, files=None) -> 'requests.Response':
        pass

    def get(self, url: str, params: dict = None) -> 'requests.Response':
        request = {
            'method': 'GET',
            'url': url,
            'params': params
        }
        self.requests.append(request)
        response = requests.Response()
        response.status_code = 200
        urls = {
            '/qrs/app': '',
            '/qrs/app/': '',
            'other download': ''
        }
        return response

    def post(self, url: str, params: dict = None, data: 'Union[dict, list]' = None, files=None) -> 'requests.Response':
        request = {
            'method': 'POST',
            'url': url,
            'params': params,
            'data': data,
            'files': files
        }
        self.requests.append(request)
        response = requests.Response()
        response._content = ''
        response.status_code = 200
        return response

    def put(self, url: str, params: dict = None, data: 'Union[dict, list]' = None) -> 'requests.Response':
        request = {
            'method': 'PUT',
            'url': url,
            'params': params,
            'data': data
        }
        self.requests.append(request)
        response = requests.Response()
        response._content = ''
        response.status_code = 200
        return response

    def delete(self, url: str, params: dict = None) -> 'requests.Response':
        request = {
            'method': 'DELETE',
            'url': url,
            'params': params
        }
        self.requests.append(request)
        response = requests.Response()
        response._content = ''
        response.status_code = 200
        return response


class FakeAppSession(orm.AppSession):
    """
    This is a fake session that mocks out the actual API wrapper calls to the Qlik Sense controller. Most API calls are
    routed through this class.

    Args:
        controller: a Controller class that provides an interface over the QRS API
    """
    def __init__(self, controller: 'orm.Controller'):
        super().__init__(controller=controller)
        self.controller = None
        self.requests = list()
        self.default_response = requests.Response()

    def query(self, query_string: str) -> 'List[models.App]':
        request = {
            'method': 'GET',
            'url': self.url,
            'params': {'filter': query_string}
        }
        self.requests.append(request)
        app = {
            'guid': 'abc',
            'name': 'name'
        }
        return self.schema.loads(json.dumps(app))

    def get(self, guid: str) -> 'models.App':
        request = {
            'method': 'GET',
            'url': f'{self.url}/{guid}'
        }
        self.requests.append(request)
        app = {
            'guid': 'abc',
            'name': 'name'
        }
        return self.schema.loads(json.dumps(app))

    def update(self, app: 'models.App', updates: dict) -> 'requests.Response':
        request = {
            'method': 'PUT',
            'url': f'{self.url}/{app.guid}',
            'data': updates
        }
        self.requests.append(request)
        return self.default_response

    def delete(self, app: 'models.App') -> 'requests.Response':
        request = {
            'method': 'DELETE',
            'url': f'{self.url}/{app.guid}'
        }
        self.requests.append(request)
        return self.default_response

    def reload(self, app: 'models.App') -> 'requests.Response':
        request = {
            'method': 'POST',
            'url': f'{self.url}/{app.guid}/reload'
        }
        self.requests.append(request)
        return self.default_response

    def copy(self, app: 'models.App', name: str = None) -> 'requests.Response':
        params = {'name': name} if name else None
        request = {
            'method': 'POST',
            'url': f'{self.url}/{app.guid}/copy',
            'params': params
        }
        self.requests.append(request)
        return self.default_response

    def export(self, app: 'models.App') -> 'requests.Response':
        token = uuid.uuid4()
        request = {
            'method': 'POST',
            'url': f'{self.url}/{app.guid}/export/{token}'
        }
        self.requests.append(request)
        return self.default_response

    def publish(self, app: 'models.App', stream: 'models.Stream') -> 'requests.Response':
        params = {'stream': stream.guid}
        request = {
            'method': 'PUT',
            'url': f'{self.url}/{app.guid}/publish',
            'params': params
        }
        self.requests.append(request)
        return self.default_response

    def replace(self, app: 'models.App', app_to_replace: 'models.App') -> 'requests.Response':
        params = {'app': app_to_replace.guid}
        request = {
            'method': 'PUT',
            'url': f'{self.url}/{app.guid}/replace',
            'params': params
        }
        self.requests.append(request)
        return self.default_response

    def upload(self, file, params: dict) -> 'requests.Response':
        request = {
            'method': 'POST',
            'url': f'{self.url}/upload',
            'params': params,
            'data': file
        }
        self.requests.append(request)
        return self.default_response
