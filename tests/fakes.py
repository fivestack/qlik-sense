import logging
from typing import Optional

import requests

from .conftest import services, models, Client


class FakeAppService(services.AppService):
    """
    This is a fake service that mocks out the actual API wrapper calls to the Qlik Sense Client class. All app service
    API calls are routed through this class. Hence, this replaces external calls from the system. Each request is
    logged in the instance so that they can be inspected by the unit tests. Mock objects are returned as necessary.
    """
    def __init__(self):
        client = Client(
            schema='http',
            host='local_host',
            port=80,
            log_name='qlik_sense_client_test',
            verbosity=logging.DEBUG
        )
        super().__init__(client=client)
        self.requests = []
        self._apps = list()
        self.client.app = self

    def _call(self, request: 'models.QSAPIRequest') -> 'requests.Response':
        self.requests.append(request)
        response = requests.Response()
        response.status_code = 100
        return response

    def get_fake_app(self, id: str) -> 'Optional[models.App]':
        return next((a for a in self._apps if a.id == id), None)

    def add_fake_app(self, app_id: str, app_name: str, stream_id: str = None, stream_name: str = None):
        if stream_id:
            stream = models.Stream(id=stream_id, name=stream_name)
            app = models.App(id=app_id, name=app_name, stream=stream)
        else:
            app = models.App(id=app_id, name=app_name)
        self._apps.append(app)
