from typing import TYPE_CHECKING, List
import json

import uuid

from .conftest import orm, abstract_repositories, unit_of_work

if TYPE_CHECKING:
    from .conftest import models


class FakeAppSession(orm.AppSession):
    """
    This is a fake session that mocks out the actual API wrapper calls to the Qlik Sense Controller class. All API
    calls are routed through this class. Hence, this replaces external calls from the system. Each request is logged
    in the instance so that they can be inspected by the unit tests. Mock objects are returned as necessary.

    Args:
        controller: a Controller class that provides an interface over the QRS API
    """
    def __init__(self, controller: 'orm.Controller'):
        super().__init__(controller=controller)
        self.controller = None
        self.requests = list()

    def query(self, query_string: str):
        request = {
            'method': 'GET',
            'url': self.url,
            'params': {'filter': query_string}
        }
        self.requests.append(request)

    def query_one(self, guid: str):
        request = {
            'method': 'GET',
            'url': f'{self.url}/{guid}'
        }
        self.requests.append(request)

    def update(self, app: 'models.App', updates: dict):
        request = {
            'method': 'PUT',
            'url': f'{self.url}/{app.guid}',
            'data': updates
        }
        self.requests.append(request)

    def delete(self, app: 'models.App'):
        request = {
            'method': 'DELETE',
            'url': f'{self.url}/{app.guid}'
        }
        self.requests.append(request)

    def reload(self, app: 'models.App'):
        request = {
            'method': 'POST',
            'url': f'{self.url}/{app.guid}/reload'
        }
        self.requests.append(request)

    def copy(self, app: 'models.App', name: str = None):
        params = {'name': name} if name else None
        request = {
            'method': 'POST',
            'url': f'{self.url}/{app.guid}/copy',
            'params': params
        }
        self.requests.append(request)

    def export(self, app: 'models.App') -> str:
        token = uuid.uuid4()
        request = {
            'method': 'POST',
            'url': f'{self.url}/{app.guid}/export/{token}'
        }
        self.requests.append(request)
        return 'path/to/download'

    def publish(self, app: 'models.App', stream: 'models.Stream'):
        params = {'stream': stream.guid}
        request = {
            'method': 'PUT',
            'url': f'{self.url}/{app.guid}/publish',
            'params': params
        }
        self.requests.append(request)

    def replace(self, app: 'models.App', app_to_replace: 'models.App'):
        params = {'app': app_to_replace.guid}
        request = {
            'method': 'PUT',
            'url': f'{self.url}/{app.guid}/replace',
            'params': params
        }
        self.requests.append(request)

    def upload(self, file, params: dict):
        request = {
            'method': 'POST',
            'url': f'{self.url}/upload',
            'params': params,
            'data': file
        }
        self.requests.append(request)

    def download_file(self, url: str) -> iter:
        file = ['first line', 'second line', 'third line']
        for line in file:
            yield line


class FakeAppRepository(abstract_repositories.AbstractAppRepository):

    def __init__(self, session: 'orm.AppSession'):
        super().__init__()
        self.session = session
        self._apps = set()

    def _query(self, app_name: str, stream_name: str) -> 'List[models.App]':
        query_string = f"name eq '{app_name}' and stream.name eq '{stream_name}'"
        self.session.query(query_string=query_string)
        return next((
            a for a in self._apps
            if a.name == app_name
            and a.stream.name == stream_name
        ), None)

    def _get(self, guid: str) -> 'models.App':
        self.session.query_one(guid=guid)
        return next((a for a in self._apps if a.guid == guid), None)

    def _remove(self, app: 'models.App'):
        self.session.delete(app=app)
        self._apps.remove(app)

    def _add(self, app: 'models.App'):
        self._apps.add(app)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self, controller: 'orm.Controller'):
        app_session = FakeAppSession(controller=controller)
        self.init_repositories(apps=FakeAppRepository(session=app_session))
