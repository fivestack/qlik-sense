from typing import TYPE_CHECKING
import json

from qlik_sense import abstract_repositories, models

if TYPE_CHECKING:
    from qlik_sense.session import Session


class QlikSenseAppRepository(abstract_repositories.AbstractAppRepository):

    def __init__(self, session: 'Session'):
        super().__init__()
        self.session = session

    def _get(self, guid: str) -> 'models.App':
        app = json.dumps(self.session.get(url=f'/qrs/app/{guid}').json())
        return models.App(guid=app['app'],
                          name=app['name'])

    def _get_by_name_and_stream(self, app_name: str, stream_name: str) -> 'models.App':
        params = {'filter': f"name eq '{app_name}' and stream.name eq '{stream_name}'"}
        response = self.session.get(url='qrs/app', params=params)
        app = json.loads(response.json())
        return self._get(guid=app[0]['id'])

    def _add(self, app: 'models.App', file_name: str):
        params = {'name': app.name, 'keepdata': False}
        self.session.upload(url='/qrs/app/upload', params=params, file_name=file_name)

    def _update(self, app: 'models.App', updates: dict):
        self.session.put(url=f'/qrs/app/{app.guid}', data=updates)

    def _remove(self, app: 'models.App'):
        self.session.delete(url=f'/qrs/app/{app.guid}')
