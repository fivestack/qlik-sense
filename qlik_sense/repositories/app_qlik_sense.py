import json
from typing import TYPE_CHECKING

from qlik_sense import abstract_repositories
from qlik_sense.domain import models

if TYPE_CHECKING:
    from qlik_sense.orm import session


class QlikSenseAppRepository(abstract_repositories.AbstractAppRepository):

    def __init__(self, session: session.Session):
        super().__init__()
        self.session = session

    def _get(self, guid: str) -> 'models.App':
        return models.App(guid=guid)

    def _get_by_name_and_stream(self, app_name: str, stream_name: str) -> 'models.App':
        response = self.session.get(url='qrs/app',
                                    params={'filter': f"name eq '{app_name}' and stream.name eq '{stream_name}'"})
        app = json.loads(response.json())
        guid = app[0]['id']
        return models.App(guid=guid)

    def _add(self, dataset_container: 'models.App'):
        pass
