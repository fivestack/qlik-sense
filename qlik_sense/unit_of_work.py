"""
The unit of work is an abstraction over the repositories and controller. In a more mature application, it will
also serve the same purpose as a database transaction. However, all current functionality of this application
are singletons (correspond to a single api call), so there is no need for that.
"""
import abc
from typing import TYPE_CHECKING

from qlik_sense import repositories, orm

if TYPE_CHECKING:
    from qlik_sense import abstract_repositories


class AbstractUnitOfWork(abc.ABC):
    """
    Collects all repositories to be worked on. Also contains a single Controller instance for when a repository
    is not needed (e.g., a file download link).
    """
    _apps = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def init_repositories(self, apps: 'abstract_repositories.AbstractAppRepository'):
        """
        Sets up all repositories for the unit of work.

        Args:
            apps: an App repository
        """
        self._apps = apps

    @property
    def apps(self) -> 'abstract_repositories.AbstractAppRepository':
        """
        Provides a handle for the relevant App repository

        Returns: an App repository
        """
        return self._apps


class QlikSenseUnitOfWork(AbstractUnitOfWork):
    """
    An implementation of an AbstractUnitOfWork. Given a controller, it will setup all relevant repositories.

    Args:
        controller: a Controller instance that connects to the QlikSense APIs
    """
    def __init__(self, controller: 'orm.Controller'):
        app_session = orm.AppSession(controller=controller)
        self.init_repositories(apps=repositories.QlikSenseAppRepository(session=app_session))
