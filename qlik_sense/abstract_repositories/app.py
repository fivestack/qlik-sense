import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qlik_sense.domain import models


class AbstractAppRepository(abc.ABC):
    """
    This repository contains methods to work with QlikSense apps
    """
    def __init__(self):
        self.seen = set()

    def get(self, guid: str) -> 'models.App':
        obj = self._get(guid=guid)
        if obj:
            self.seen.add(obj)
        return obj

    def get_by_name_and_stream(self, app_name: str, stream_name: str) -> 'models.App':
        obj = self._get_by_name_and_stream(app_name=app_name, stream_name=stream_name)
        if obj:
            self.seen.add(obj)
        return obj

    def add(self, app: 'models.App'):
        self._add(app)
        self.seen.add(app)

    @abc.abstractmethod
    def _get(self, guid: str) -> 'models.App':
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_name_and_stream(self, app_name: str, stream_name: str) -> 'models.App':
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, app: 'models.App'):
        raise NotImplementedError
