"""
This module provides functionality for working with Qlik Sense apps when this package is imported as a library.
"""
from typing import TYPE_CHECKING

from qlik_sense.orm.session import Session
from qlik_sense.service_layer import unit_of_work, services

if TYPE_CHECKING:
    from qlik_sense.domain import models


class QlikSense:
    """
    This is a controller for the functionality in this library.

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

    def reload_app(self, guid: str):
        """
        Reloads an app given its guid.

        Args:
            guid: guid of the app on the server
        """
        services.reload_app(guid=guid, uow=self.uow)
