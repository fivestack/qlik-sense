import abc
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from qlik_sense import models
    from qlik_sense.orm.app import AppSession


class AbstractAppRepository(abc.ABC):

    session: 'AppSession' = None

    def __init__(self):
        self.seen = set()

    def query(self, app_name: str, stream_name: str) -> 'List[models.App]':
        objs = self._query(app_name=app_name, stream_name=stream_name)
        if objs:
            for obj in objs:
                self.seen.add(obj)
        return objs

    def get(self, guid: str) -> 'models.App':
        obj = self._get(guid=guid)
        if obj:
            self.seen.add(obj)
        return obj

    def update(self, app: 'models.App', updates: dict):
        self._update(app=app, updates=updates)
        self.seen.add(app)

    def remove(self, app: 'models.App'):
        self._remove(app=app)
        self.seen.add(app)

    def add(self, app: 'models.App'):
        self._add(app=app)

    @abc.abstractmethod
    def _query(self, app_name: str, stream_name: str) -> 'List[models.App]':
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, guid: str) -> 'models.App':
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(self, app: 'models.App'):
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, app: 'models.App'):
        raise NotImplementedError
