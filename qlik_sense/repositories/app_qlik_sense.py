from typing import TYPE_CHECKING, List

from qlik_sense import abstract_repositories, models

if TYPE_CHECKING:
    from qlik_sense.orm.app import AppSession


class QlikSenseAppRepository(abstract_repositories.AbstractAppRepository):
    """
    This is an implementation of the AbstractAppRepository that wires in the QRS API via an AppSession instance.

    Args:
        session: an AppSession instance that contains a Controller to connect to the QRS API
    """
    def __init__(self, session: 'AppSession'):
        super().__init__()
        self.session = session

    def _query(self, app_name: str, stream_name: str) -> 'List[models.App]':
        """
        Queries the QRS API for an app by its name and the name of the stream it's in.

        .. note::
            This is currently very limited in functionality. It can be augmented in the future to be more
            flexible in its search criteria. However, it currently requires a single app name and a single
            stream name. And it searches based on equality, not wildcard. This likely identifies a single
            application in most scenarios.

        Args:
            app_name: the exact name of the app to search for
            stream_name: the exact name of the stream that contains the app

        Returns: a list of apps that fit the criteria (which is likely one app, see the note)
        """
        query_string = f"name eq '{app_name}' and stream.name eq '{stream_name}'"
        return self.session.query(query_string=query_string)

    def _get(self, guid: str) -> 'models.App':
        """
        Returns an App based on its guid

        Args:
            guid: the guid of the App

        Returns: the App
        """
        return self.session.get(guid=guid)

    def _update(self, app: 'models.App', updates: dict):
        """
        Updates the provided attributes on an app

        Args:
            app: the app to update
            updates: the updates to make
        """
        self.session.update(app=app, updates=updates)

    def _remove(self, app: 'models.App'):
        """
        Deletes the app from the server

        Args:
            app: the app to delete
        """
        self.session.delete(app=app)

    def _add(self, file: iter, params: dict):
        """
        Uploads an app to the server

        Args:
            file: the file to upload
            params: parameters/attributes for the new app (e.g., name, keepdata)
        """
        self.session.upload(file=file, params=params)
