from typing import TYPE_CHECKING
from pathlib import Path
from os.path import isfile

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
            app_id: str = None, app_name: str = None, stream_id: str = None, stream_name: str = None):
    if stream_id or stream_name:
        stream = models.Stream(id=stream_id, name=stream_name)
        uow.apps.add(models.App(id=app_id, name=app_name, stream=stream))
    else:
        uow.apps.add(models.App(id=app_id, name=app_name))


class TestApp:

    uow = uow_factory()

    def setup_method(self):
        add_app(uow=self.uow, app_id='app_1', app_name='My App', stream_id='stream_1', stream_name='My Stream')
        add_app(uow=self.uow, app_id='app_2', app_name='Not My App', stream_id='stream_1', stream_name='My Stream')
        add_app(uow=self.uow, app_id='app_3', app_name='My Other App')
        self.uow.apps.session.requests = []

    def teardown_method(self):
        try:
            app = services.get_app(id='app_1', uow=self.uow)
            file = PROJECT_ROOT / Path(f'{app.name}.qvf')
            try:
                file.unlink()
            except FileNotFoundError:
                pass
            services.delete_app(id='app_1', uow=self.uow)
            services.delete_app(id='app_2', uow=self.uow)
            services.delete_app(id='app_3', uow=self.uow)
        except AttributeError:
            pass

    def test_get_app_by_name_and_stream(self):
        found_app = services.get_app_by_name_and_stream_name(app_name='My App', stream_name='My Stream', uow=self.uow)
        assert 'app_1' == found_app.id

    def test_get_app_by_guid(self):
        found_app = services.get_app(id='app_2', uow=self.uow)
        assert 'Not My App' == found_app.name

    def test_get_app_by_name_and_stream_missing(self):
        missing_app = services.get_app_by_name_and_stream_name(app_name='Another App',
                                                               stream_name='My Stream',
                                                               uow=self.uow)
        assert None is missing_app

    def test_get_app_by_guid_missing(self):
        missing_app = services.get_app(id='app_4', uow=self.uow)
        assert None is missing_app

    def test_delete_app(self):
        app = services.get_app(id='app_1', uow=self.uow)
        services.delete_app(id=app.id, uow=self.uow)
        get_app_again = services.get_app(id='app_1', uow=self.uow)
        assert None is get_app_again
        request = models.QSAPIRequest(
            method='DELETE',
            url=f'/qrs/app/{app.id}'
        )
        assert request in self.uow.apps.session.requests

    def test_reload_app(self):
        app = services.get_app(id='app_1', uow=self.uow)
        services.reload_app(id=app.id, uow=self.uow)
        request = models.QSAPIRequest(
            method='POST',
            url=f'/qrs/app/{app.id}/reload'
        )
        assert request in self.uow.apps.session.requests

    def test_copy_app(self):
        app = services.get_app(id='app_1', uow=self.uow)
        services.copy_app(id=app.id, name=app.name, uow=self.uow)
        request = models.QSAPIRequest(
            method='POST',
            url=f'/qrs/app/{app.id}/copy',
            params={'name': app.name}
        )
        assert request in self.uow.apps.session.requests

    def test_download_app(self):
        app = services.get_app(id='app_1', uow=self.uow)
        services.download_app(id=app.id, uow=self.uow)
        file = PROJECT_ROOT / Path(f'{app.name}.qvf')
        assert isfile(file.absolute())
        for request in self.uow.apps.session.requests:
            if request.method == 'POST':
                url = request.url
                assert f'qrs/app/{app.id}/export' == '/'.join(url.split('/')[1:5])

    def test_publish_app(self):
        app = services.get_app(id='app_1', uow=self.uow)
        stream = models.Stream(id='stream_1', name='My Stream')
        services.publish_app(id=app.id, stream_id=stream.id, uow=self.uow)
        request = models.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{app.id}/publish',
            params={'stream': stream.id}
        )
        assert request in self.uow.apps.session.requests

    def test_replace_app(self):
        app = services.get_app(id='app_1', uow=self.uow)
        app_to_replace = services.get_app(id='app_2', uow=self.uow)
        services.replace_app(id=app.id, id_to_replace=app_to_replace.id, uow=self.uow)
        request = models.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{app.id}/replace',
            params={'app': app_to_replace.id}
        )
        assert request in self.uow.apps.session.requests

    def test_upload_app(self):
        file_name = Path(__file__).absolute()
        app_name = 'My New App'
        services.upload_app(file_name=file_name, app_name=app_name, uow=self.uow)
        for request in self.uow.apps.session.requests:
            if request.method == 'POST':
                assert request.url == '/qrs/app/upload'
                assert request.params == {'name': app_name, 'keepdata': False}
