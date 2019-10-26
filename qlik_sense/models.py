from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from qlik_sense.session import Session


@dataclass
class App:
    guid: str = None
    name: str = None
    stream_name: str = None

    def reload(self, session: 'Session'):
        session.post(url=f'qrs/app/{self.guid}/reload')

    def publish(self, session: 'Session', stream_guid: str):
        session.put(url=f'/qrs/app/{self.guid}/publish', params={'stream': stream_guid})

    def replace(self, session: 'Session', guid: str):
        session.put(url=f'/qrs/app/{self.guid}/replace', params={'app': guid})

    def copy(self, session: 'Session', name: str = None):
        session.post(url=f'/qrs/app/{self.guid}/copy', params={'name': name})

    def download(self, session: 'Session'):
        session.download(guid=self.guid, file_name=f'{self.name}.qvf')
