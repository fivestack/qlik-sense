from typing import List
import json

import uuid

from .conftest import orm, abstract_repositories, unit_of_work
from qlik_sense.api_client import models


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

    def _call(self, request: 'models.QSAPIRequest'):
        if request.data:
            if isinstance(request.data, dict) or isinstance(request.data, list):
                request.data = json.dumps(request.data)
        self.requests.append(request)

    def query(self, query_string: str):
        request = models.QSAPIRequest(
            method='GET',
            url=f'{self.url}',
            params={'filter': query_string}
        )
        self.requests.append(request)

    def query_one(self, id: str):
        request = models.QSAPIRequest(
            method='GET',
            url=f'{self.url}/{id}'
        )
        self.requests.append(request)

    def export(self, app: 'models.App'):
        token = uuid.uuid4()
        request = models.QSAPIRequest(
            method='POST',
            url=f'{self.url}/{app.id}/export/{token}'
        )
        self.requests.append(request)

    def download_file(self, url: str) -> iter:
        file = ['first line', 'second line', 'third line']
        for line in file:
            yield bytes(line, encoding='utf-8')


class FakeAppRepository(abstract_repositories.AbstractAppRepository):

    def __init__(self, session: 'orm.AppSession'):
        super().__init__()
        self.session = session
        self._apps = set()

    def _query(self, app_name: str, stream_name: str) -> 'List[models.App]':
        query_string = f"name eq '{app_name}' and stream.name eq '{stream_name}'"
        self.session.query(query_string=query_string)
        app = next((
            a for a in self._apps
            if a.name == app_name
            and a.stream.name == stream_name
        ), None)
        return [app]

    def _get(self, id: str) -> 'models.App':
        self.session.query_one(id=id)
        return next((a for a in self._apps if a.id == id), None)

    def _remove(self, app: 'models.App'):
        self.session.delete(app=app)
        self._apps.remove(app)

    def _add(self, app: 'models.App'):
        self._apps.add(app)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self, controller: 'orm.Controller'):
        app_session = FakeAppSession(controller=controller)
        self.init_repositories(apps=FakeAppRepository(session=app_session))
