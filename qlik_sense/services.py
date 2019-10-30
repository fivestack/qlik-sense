"""
This module implements functionality from various presentation layers (API, CLI, REST API, etc.)
"""
from typing import TYPE_CHECKING
import os

from qlik_sense import models

if TYPE_CHECKING:
    from qlik_sense import unit_of_work


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


def get_app(id: str, uow: 'unit_of_work.AbstractUnitOfWork') -> 'models.App':
    """
    Returns an App object based on its guid

    Args:
        id: the guid of the app on the server
        uow: the unit of work containing the App repository

    Returns: a qlik_sense App
    """
    return uow.apps.get(id=id)


def delete_app(id: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Deletes the app from the server

    Args:
        id: the guid of the app to be deleted from the server
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(id=id)
    uow.apps.remove(app)


def reload_app(id: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Reloads the app

    Args:
        id: the guid of the app to be reloaded on the server
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(id=id)
    uow.apps.session.reload(app=app)


def copy_app(id: str, name: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Copies the app

    Args:
        id: the guid of the app to be copied on the server
        name: the name of the new app
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(id=id)
    uow.apps.session.copy(app=app, name=name)


def download_app(id: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Downloads an app from the server

    Args:
        id: the guid of the app to be downloaded from the server
        uow: the unit of work containing the App repository

    Returns: the file path to the downloaded app
    """
    app = uow.apps.get(id=id)
    download_url = uow.apps.session.export(app=app)
    file = uow.apps.session.download_file(url=download_url)
    with open(file=f'{app.name}.qvf', mode='wb') as f:
        for chunk in file:
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def publish_app(id: str, stream_id: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Publishes an app from your workspace to the provided stream

    Args:
        id: the guid of the app to be published on the server
        stream_id: the guid of the stream to which to publish the app
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(id=id)
    stream = models.Stream(id=stream_id)
    uow.apps.session.publish(app=app, stream=stream)


def replace_app(id: str, id_to_replace: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    Replaces a target app with the current app

    Args:
        id: the guid of the app to be copied on the server
        id_to_replace: the guid of the app to be replaced on the server
        uow: the unit of work containing the App repository
    """
    app = uow.apps.get(id=id)
    app_to_replace = uow.apps.get(id=id_to_replace)
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
