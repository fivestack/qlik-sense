"""
This module implements functionality from various presentation layers (API, CLI, REST API, etc.)
"""
from typing import TYPE_CHECKING
import os

from qlik_sense import models

if TYPE_CHECKING:
    from qlik_sense import unit_of_work
    import requests


def get_app_by_name_and_stream_name(app_name: str, stream_name: str,
                                    uow: 'unit_of_work.AbstractUnitOfWork') -> 'models.App':
    """
    Returns an App object based on app name and stream name

    Args:
        app_name: the name of the app
        stream_name: the name of the stream that contains the app
        uow: the unit of work containing the App repository

    Returns: a qlik_sense App
    """
    return uow.apps.query(app_name=app_name, stream_name=stream_name)[0]


def get_app(guid: str, uow: 'unit_of_work.AbstractUnitOfWork') -> 'models.App':
    """
    Returns an App object based on its guid

    Args:
        guid: the guid of the app on the server
        uow: the unit of work containing the App repository

    Returns: a qlik_sense App
    """
    return uow.apps.get(guid=guid)


def update_app(guid: str, updates: dict, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Updates the provided attributes on an application

    Args:
        guid: the guid of the app to be updated on the server
        updates: a dictionary containing the attributes to update
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(guid=guid)
    uow.apps.update(app=app, updates=updates)


def delete_app(guid: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Deletes the app from the server

    Args:
        guid: the guid of the app to be deleted from the server
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(guid=guid)
    uow.apps.remove(app)


def reload_app(guid: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Reloads the app

    Args:
        guid: the guid of the app to be reloaded on the server
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(guid=guid)
    uow.apps.session.reload(app=app)


def copy_app(guid: str, name: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Copies the app

    Args:
        guid: the guid of the app to be copied on the server
        name: the name of the new app
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(guid=guid)
    uow.apps.session.copy(app=app, name=name)


def download_app(guid: str, uow: 'unit_of_work.AbstractUnitOfWork') -> str:
    """
    Downloads an app from the server

    Args:
        guid: the guid of the app to be downloaded from the server
        uow: the unit of work containing the App repository

    Returns: the file path to the downloaded app
    """
    app = uow.apps.get(guid=guid)
    url = uow.apps.session.export(app).json()['downloadPath']
    response = uow.controller.get(url=url)
    file = _save_file(response=response, file_name=f'{app.name}.qvf')
    return file


def _save_file(response: 'requests.Response', file_name: str) -> str:
    """
    A utility function for download_app() that saves the file in the response

    Args:
        response: the response containing the file
        file_name: the name of the new file on the file server

    Returns: the file path to the downloaded app
    """
    with open(file_name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=512 << 10):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
        file = f.name
    return file


def publish_app(guid: str, stream_guid: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Publishes an app from your workspace to the provided stream

    Args:
        guid: the guid of the app to be published on the server
        stream_guid: the guid of the stream to which to publish the app
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(guid=guid)
    stream = models.Stream(guid=stream_guid)
    uow.apps.session.publish(app=app, stream=stream)


def replace_app(guid: str, guid_to_replace: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Replaces a target app with the current app

    Args:
        guid: the guid of the app to be copied on the server
        guid_to_replace: the guid of the app to be replaced on the server
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(guid=guid)
    app_to_replace = uow.apps.get(guid=guid_to_replace)
    uow.apps.session.replace(app=app, app_to_replace=app_to_replace)


class _FileUpload:
    """
    A utility class for upload_app()

    Args:
        file_name: the name of the file
        chunk_size: the upload size for each chunk
    """
    def __init__(self, file_name: str, chunk_size: int = 512):
        self._filename = file_name
        self._chunk_size = chunk_size << 10
        self._total_size = os.path.getsize(file_name)
        self._read_so_far = 0

    def __iter__(self):
        """
        An iterator that provides a chunk of the file at a time

        Returns: a file chunk
        """
        with open(self._filename, 'rb') as file:
            while True:
                data = file.read(self._chunk_size)
                if not data:
                    break
                self._read_so_far += len(data)
                yield data

    def __len__(self):
        """
        A convenience method

        Returns: the size of the whole file
        """
        return self._total_size


def upload_app(file_name: str, app_name: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Uploads an app file to the server

    Args:
        file_name: name of the app file
        app_name: name of the new app on the server
        uow: the unit of work containing the App repository
    """
    file = _FileUpload(file_name=file_name)
    params = {'name': app_name, 'keepdata': False}
    uow.apps.session.upload(file=file, params=params)
