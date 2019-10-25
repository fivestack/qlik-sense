from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qlik_sense.service_layer import unit_of_work


def reload_app(guid: str, uow: 'unit_of_work.AbstractUnitOfWork'):
    app = uow.apps.get(guid=guid)
    uow.session.post(url=f'qrs/app/{app.guid}/reload')
