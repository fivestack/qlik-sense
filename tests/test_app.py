from typing import TYPE_CHECKING

import pytest

from .conftest import orm, models, services
from .fakes import FakeUnitOfWork

if TYPE_CHECKING:
    from .conftest import unit_of_work


@pytest.fixture
def uow() -> 'unit_of_work.AbstractUnitOfWork':
    controller = orm.Controller(log_name='qlik_sense_test',
                                verbosity='DEBUG',
                                schema='https',
                                host='localhost',
                                port=80)
    return FakeUnitOfWork(controller=controller)


def test_get_app_by_name_and_stream_name(uow):
    my_stream = models.Stream(guid='stream_1', name='My Stream')
    my_app = models.App(guid='app_1', name='My App', stream=my_stream)
    my_other_app = models.App(guid='app_2', name='Not My App', stream=my_stream)
    my_other_app_with_no_stream = models.App(guid='app_3', name='My Other App')
    uow.apps.add(my_app)
    uow.apps.add(my_other_app)
    uow.apps.add(my_other_app_with_no_stream)
    found_app = services.get_app_by_name_and_stream_name(app_name='My App', stream_name='My Stream', uow=uow)
    assert 'app_1' == found_app.guid
