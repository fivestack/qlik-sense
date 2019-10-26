import abc
from typing import TYPE_CHECKING

from qlik_sense import repositories

if TYPE_CHECKING:
    from qlik_sense import abstract_repositories
    from qlik_sense.session import Session


class AbstractUnitOfWork(abc.ABC):

    session = None
    controller = None
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

    def __init__(self, session: 'Session'):
        self.session = session
        self.init_repositories(apps=repositories.QlikSenseAppRepository(session))
