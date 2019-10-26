"""
This module provides functionality for working with Qlik Sense apps when this package is imported as a library.
"""
from typing import TYPE_CHECKING

from qlik_sense import services, unit_of_work
from qlik_sense.session import Session

if TYPE_CHECKING:
    from qlik_sense import models


class QlikSense:
    """
    This is the entry point for the functionality in this library.

    Args:
        host: the url for the QS instance
        certificate: the file path to the cert on the local machine
    """
    def __init__(self, host: str, certificate: str):
        session = Session(log_name='qsapi',
                          verbosity='INFO',
                          schema='https',
                          host=host,
                          port=4242,
                          certificate=certificate,
                          verify=False)
        self.uow = unit_of_work.QlikSenseUnitOfWork(session=session)

    def get_app(self, guid: str) -> 'models.App':
        """
        Provides an App object given its guid.

        Args:
            guid: guid of the app on the server

        Returns: a Qlik Sense App object
        """
        return self.uow.apps.get(guid=guid)

    def get_app_by_name_and_stream(self, app_name: str, stream_name: str) -> 'models.App':
        """
        Provides an App object given its name and the name of the stream it's in.

        Args:
            app_name: the exact name of the app on the server
            stream_name: the exact name of the stream on the server

        Returns: a Qlik Sense App object
        """
        return self.uow.apps.get_by_name_and_stream(app_name=app_name, stream_name=stream_name)

    def upload_app(self, file_name: str, app_name: str):
        """
        Downloads an app given its guid.

        Args:
            file_name: name for the file to upload
            app_name: name for the app
        """
        services.upload_app(file_name=file_name, app_name=app_name, uow=self.uow)

    def update_app(self, guid: str, updates: dict):
        """
        Updates an app given its guid and the data to be updated.

        Args:
            guid: guid of the app on the server
            updates: attributes to update
        """
        services.update_app(guid=guid, updates=updates, uow=self.uow)

    def delete_app(self, guid: str):
        """
        Deletes an app given its guid

        Args:
            guid: guid of the app on the server
        """
        services.delete_app(guid=guid, uow=self.uow)

    def reload_app(self, guid: str):
        """
        Reloads an app given its guid.

        Args:
            guid: guid of the app on the server
        """
        services.reload_app(guid=guid, uow=self.uow)

    def publish_app(self, guid: str, stream_guid: str):
        """
        Publishes an app given its guid.

        Args:
            guid: guid of the app on the server
            stream_guid: guid of the stream on the server
        """
        services.publish_app(guid=guid, stream_guid=stream_guid, uow=self.uow)

    def replace_app(self, guid: str, guid_to_replace: str):
        """
        Replaces one app <guid_to_replace> with another app <guid>

        Args:
            guid: guid of the app to copy
            guid_to_replace: guid of the app to replace
        """
        services.replace_app(guid=guid, guid_to_replace=guid_to_replace, uow=self.uow)

    def copy_app(self, guid: str, name: str = None):
        """
        Copies an app given its guid.

        Args:
            guid: guid of the app on the server
            name: optional name for the new app
        """
        services.copy_app(guid=guid, name=name, uow=self.uow)

    def download_app(self, guid: str):
        """
        Downloads an app given its guid.

        Args:
            guid: guid of the app on the server
        """
        services.download_app(guid=guid, uow=self.uow)
