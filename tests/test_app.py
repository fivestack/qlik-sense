from typing import TYPE_CHECKING
from pathlib import Path
from os.path import isfile

import pytest

from .conftest import orm, models, services, PROJECT_ROOT
from .fakes import FakeUnitOfWork

if TYPE_CHECKING:
    from .conftest import unit_of_work


def uow_factory() -> 'unit_of_work.AbstractUnitOfWork':
    controller = orm.Controller(log_name='qlik_sense_test',
                                verbosity='DEBUG',
                                schema='https',
                                host='localhost',
                                port=80)
    return FakeUnitOfWork(controller=controller)


def add_app(uow: 'unit_of_work.AbstractUnitOfWork',
            app_guid: str = None, app_name: str = None, stream_guid: str = None, stream_name: str = None):
    if stream_guid or stream_name:
        stream = models.Stream(guid=stream_guid, name=stream_name)
        uow.apps.add(models.App(guid=app_guid, name=app_name, stream=stream))
    else:
        uow.apps.add(models.App(guid=app_guid, name=app_name))


class TestApp:

    uow = uow_factory()

    def setup_method(self):
        add_app(uow=self.uow, app_guid='app_1', app_name='My App', stream_guid='stream_1', stream_name='My Stream')
        add_app(uow=self.uow, app_guid='app_2', app_name='Not My App', stream_guid='stream_1', stream_name='My Stream')
        add_app(uow=self.uow, app_guid='app_3', app_name='My Other App')
        self.uow.apps.session.requests = []

    def teardown_method(self):
        try:
            app = services.get_app(guid='app_1', uow=self.uow)
            file = PROJECT_ROOT / Path(f'{app.name}.qvf')
            try:
                file.unlink()
            except FileNotFoundError:
                pass
            services.delete_app(guid='app_1', uow=self.uow)
            services.delete_app(guid='app_2', uow=self.uow)
            services.delete_app(guid='app_3', uow=self.uow)
        except AttributeError:
            pass

    def test_get_app_by_name_and_stream(self):
        found_app = services.get_app_by_name_and_stream_name(app_name='My App', stream_name='My Stream', uow=self.uow)
        assert 'app_1' == found_app.guid

    def test_get_app_by_guid(self):
        found_app = services.get_app(guid='app_2', uow=self.uow)
        assert 'Not My App' == found_app.name

    def test_get_app_by_name_and_stream_missing(self):
        missing_app = services.get_app_by_name_and_stream_name(app_name='Another App',
                                                               stream_name='My Stream',
                                                               uow=self.uow)
        assert None is missing_app

    def test_get_app_by_guid_missing(self):
        missing_app = services.get_app(guid='app_4', uow=self.uow)
        assert None is missing_app

    def test_update_app(self):
        app = services.get_app(guid='app_1', uow=self.uow)
        updates = {'name': 'My Altered App'}
        services.update_app(guid=app.guid, updates=updates, uow=self.uow)
        assert app.name == 'My Altered App'
        request = {
            'method': 'PUT',
            'url': f'/qrs/app/{app.guid}',
            'data': updates
        }
        assert request in self.uow.apps.session.requests

    def test_update_app_with_extra_attribute(self):
        app = services.get_app(guid='app_1', uow=self.uow)
        updates = {'name': 'My Altered App', 'this_other_attribute': 'I set this'}
        services.update_app(guid=app.guid, updates=updates, uow=self.uow)
        assert app.name == 'My Altered App'
        with pytest.raises(AttributeError):
            assert app.this_other_attribute is None
        request = {
            'method': 'PUT',
            'url': f'/qrs/app/{app.guid}',
            'data': updates
        }
        assert request in self.uow.apps.session.requests

    def test_delete_app(self):
        app = services.get_app(guid='app_1', uow=self.uow)
        services.delete_app(guid=app.guid, uow=self.uow)
        get_app_again = services.get_app(guid='app_1', uow=self.uow)
        assert None is get_app_again
        request = {
            'method': 'DELETE',
            'url': f'/qrs/app/{app.guid}'
        }
        assert request in self.uow.apps.session.requests

    def test_reload_app(self):
        app = services.get_app(guid='app_1', uow=self.uow)
        services.reload_app(guid=app.guid, uow=self.uow)
        request = {
            'method': 'POST',
            'url': f'/qrs/app/{app.guid}/reload'
        }
        assert request in self.uow.apps.session.requests

    def test_copy_app(self):
        app = services.get_app(guid='app_1', uow=self.uow)
        services.copy_app(guid=app.guid, name=app.name, uow=self.uow)
        request = {
            'method': 'POST',
            'url': f'/qrs/app/{app.guid}/copy',
            'params': {'name': app.name}
        }
        assert request in self.uow.apps.session.requests

    def test_download_app(self):
        app = services.get_app(guid='app_1', uow=self.uow)
        services.download_app(guid=app.guid, uow=self.uow)
        file = PROJECT_ROOT / Path(f'{app.name}.qvf')
        assert isfile(file.absolute())
        for request in self.uow.apps.session.requests:
            if request['method'] == 'POST':
                url = request['url']
                assert f'qrs/app/{app.guid}/export' == '/'.join(url.split('/')[1:5])

    def test_publish_app(self):
        app = services.get_app(guid='app_1', uow=self.uow)
        stream = models.Stream(guid='stream_1', name='My Stream')
        services.publish_app(guid=app.guid, stream_guid=stream.guid, uow=self.uow)
        request = {
            'method': 'PUT',
            'url': f'/qrs/app/{app.guid}/publish',
            'params': {'stream': stream.guid}
        }
        assert request in self.uow.apps.session.requests

    def test_replace_app(self):
        app = services.get_app(guid='app_1', uow=self.uow)
        app_to_replace = services.get_app(guid='app_2', uow=self.uow)
        services.replace_app(guid=app.guid, guid_to_replace=app_to_replace.guid, uow=self.uow)
        request = {
            'method': 'PUT',
            'url': f'/qrs/app/{app.guid}/replace',
            'params': {'app': app_to_replace.guid}
        }
        assert request in self.uow.apps.session.requests

    def test_upload_app(self):
        file_name = Path(__file__).absolute()
        app_name = 'My New App'
        services.upload_app(file_name=file_name, app_name=app_name, uow=self.uow)
        for request in self.uow.apps.session.requests:
            if request['method'] == 'POST':
                assert request['url'] == '/qrs/app/upload'
                assert request['params'] == {'name': app_name, 'keepdata': False}
