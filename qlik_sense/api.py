"""
This module provides functionality for working with Qlik Sense apps when this package is imported as a library.
"""
from typing import TYPE_CHECKING

from qlik_sense import services, unit_of_work, orm

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
        controller = orm.Controller(log_name='qlik_sense',
                                    verbosity='INFO',
                                    schema='https',
                                    host=host,
                                    port=4242,
                                    certificate=certificate,
                                    verify=False)
        self.uow = unit_of_work.QlikSenseUnitOfWork(controller=controller)

    def get_app_by_name_and_stream(self, app_name: str, stream_name: str) -> 'models.App':
        """
        Provides an App object given its name and the name of the stream it's in

        Args:
            app_name: the exact name of the app on the server
            stream_name: the exact name of the stream on the server

        Returns: a Qlik Sense App object
        """
        return services.get_app_by_name_and_stream_name(app_name=app_name, stream_name=stream_name, uow=self.uow)

    def get_app(self, guid: str) -> 'models.App':
        """
        Provides an App object given its guid

        Args:
            guid: guid of the app on the server

        Returns: a Qlik Sense App object
        """
        return services.get_app(guid=guid, uow=self.uow)

    def delete_app(self, app: 'models.App'):
        """
        Deletes an app

        Args:
            app: app to delete from the server
        """
        services.delete_app(guid=app.id, uow=self.uow)

    def reload_app(self, app: 'models.App'):
        """
        Reloads an app

        Args:
            app: app to reload
        """
        services.reload_app(guid=app.id, uow=self.uow)

    def copy_app(self, app: 'models.App', name: str = None):
        """
        Copies an app

        Args:
            app: app to copy
            name: optional name for the new app
        """
        services.copy_app(guid=app.id, name=name, uow=self.uow)

    def download_app(self, app: 'models.App'):
        """
        Downloads an app

        Args:
            app: app to download
        """
        services.download_app(guid=app.id, uow=self.uow)

    def publish_app(self, app: 'models.App', stream: 'models.Stream'):
        """
        Publishes an app given a stream

        Args:
            app: app to publish
            stream: stream to publish the app to
        """
        services.publish_app(guid=app.id, stream_guid=stream.id, uow=self.uow)

    def replace_app(self, app: 'models.App', app_to_replace: 'models.App'):
        """
        Replaces one app with another app

        Args:
            app: app to copy
            app_to_replace: app to replace
        """
        services.replace_app(guid=app.id, guid_to_replace=app_to_replace.id, uow=self.uow)

    def upload_app(self, file_name: str, app_name: str):
        """
        Downloads an app given its guid.

        Args:
            file_name: name for the file to upload
            app_name: name for the app
        """
        services.upload_app(file_name=file_name, app_name=app_name, uow=self.uow)
