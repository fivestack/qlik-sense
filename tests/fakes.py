from typing import Optional

import requests

from .conftest import services, app, stream, user, util, fake_client


class FakeAppService(services.AppService):
    """
    This is a fake service that mocks out the actual API wrapper calls to the Qlik Sense Client class. All app service
    API calls are routed through this class. Hence, this replaces external calls from the system. Each request is
    logged in the instance so that they can be inspected by the unit tests. Mock objects are returned as necessary.
    """
    def __init__(self):
        super().__init__(client=fake_client)
        self.requests = []
        self._apps = list()
        self.client.app = self

    def _call(self, request: 'util.QSAPIRequest') -> 'requests.Response':
        self.requests.append(request)
        response = requests.Response()
        response.status_code = 100
        return response

    def get_fake_app(self, id: str) -> 'Optional[app.AppCondensed]':
        return next((a for a in self._apps if a.id == id), None)

    def add_fake_app(self, app_id: str, app_name: str, stream_id: str = None, stream_name: str = None):
        if stream_id:
            new_stream = stream.StreamCondensed(id=stream_id, name=stream_name)
            new_app = app.AppCondensed(id=app_id, name=app_name, stream=new_stream)
        else:
            new_app = app.AppCondensed(id=app_id, name=app_name)
        self._apps.append(new_app)


class FakeStreamService(services.StreamService):
    """
    This is a fake service that mocks out the actual API wrapper calls to the Qlik Sense Client class. All stream service
    API calls are routed through this class. Hence, this replaces external calls from the system. Each request is
    logged in the instance so that they can be inspected by the unit tests. Mock objects are returned as necessary.
    """
    def __init__(self):
        super().__init__(client=fake_client)
        self.requests = []
        self._streams = list()
        self.client.stream = self

    def _call(self, request: 'util.QSAPIRequest') -> 'requests.Response':
        self.requests.append(request)
        response = requests.Response()
        response.status_code = 100
        return response

    def get_fake_stream(self, id: str) -> 'Optional[stream.StreamCondensed]':
        return next((s for s in self._streams if s.id == id), None)

    def add_fake_stream(self, id: str = None, name: str = None):
        new_stream = stream.StreamCondensed(id=id, name=name)
        self._streams.append(new_stream)


class FakeUserService(services.UserService):
    """
    This is a fake service that mocks out the actual API wrapper calls to the Qlik Sense Client class. All user service
    API calls are routed through this class. Hence, this replaces external calls from the system. Each request is
    logged in the instance so that they can be inspected by the unit tests. Mock objects are returned as necessary.
    """
    def __init__(self):
        super().__init__(client=fake_client)
        self.requests = []
        self._users = list()
        self.client.user = self

    def _call(self, request: 'util.QSAPIRequest') -> 'requests.Response':
        self.requests.append(request)
        response = requests.Response()
        response.status_code = 100
        return response

    def get_fake_user(self, id: str) -> 'Optional[user.UserCondensed]':
        return next((u for u in self._users if u.id == id), None)

    def add_fake_user(self, id: str = None, name: str = None):
        new_user = user.UserCondensed(id=id, name=name)
        self._users.append(new_user)
