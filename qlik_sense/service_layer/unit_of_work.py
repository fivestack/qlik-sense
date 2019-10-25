import abc
from typing import TYPE_CHECKING

from qlik_sense import repositories

if TYPE_CHECKING:
    from qlik_sense import abstract_repositories


class AbstractUnitOfWork(abc.ABC):

    session = None
    _apps = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def init_repositories(self, apps: 'abstract_repositories.AbstractAppRepository'):
        self._apps = apps

    @property
    def apps(self) -> 'abstract_repositories.AbstractAppRepository':
        return self._apps


class QlikSenseUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session):
        self.session = session
        self.init_repositories(apps=repositories.QlikSenseAppRepository(self.session))
