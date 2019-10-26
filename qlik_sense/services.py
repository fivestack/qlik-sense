from typing import TYPE_CHECKING

from qlik_sense import models

if TYPE_CHECKING:
    from qlik_sense import unit_of_work


def upload_app(file_name: str, app_name: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = models.App(name=app_name)
    uow.apps.add(app=app, file_name=file_name)


def update_app(guid: str, updates: dict, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = uow.apps.get(guid=guid)
    uow.apps.update(app=app, updates=updates)


def delete_app(guid: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = uow.apps.get(guid=guid)
    uow.apps.remove(app)


def reload_app(guid: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = uow.apps.get(guid=guid)
    app.reload(session=uow.session)


def publish_app(guid: str, stream_guid: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = uow.apps.get(guid=guid)
    app.publish(session=uow.session, stream_guid=stream_guid)


def replace_app(guid: str, guid_to_replace: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = uow.apps.get(guid=guid)
    app.replace(session=uow.session, guid=guid_to_replace)


def copy_app(guid: str, name: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = uow.apps.get(guid=guid)
    app.copy(session=uow.session, name=name)


def download_app(guid: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = uow.apps.get(guid=guid)
    app.download(session=uow.session)
