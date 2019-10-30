from pathlib import Path
from os.path import isfile

from .conftest import models, Client, PROJECT_ROOT


def client_factory() -> 'Client':
    return Client(log_name='qlik_sense_test',
                  verbosity='DEBUG',
                  schema='https',
                  host='localhost',
                  port=80)


def add_app(client: 'Client',
            app_id: str = None, app_name: str = None, stream_id: str = None, stream_name: str = None):
    if stream_id or stream_name:
        stream = models.Stream(id=stream_id, name=stream_name)
        uow.apps.add(models.App(id=app_id, name=app_name, stream=stream))
    else:
        uow.apps.add(models.App(id=app_id, name=app_name))


class TestApp:

    app_service = client_factory().app

    def setup_method(self):
        add_app(uow=self.uow, app_id='app_1', app_name='My App', stream_id='stream_1', stream_name='My Stream')
        add_app(uow=self.uow, app_id='app_2', app_name='Not My App', stream_id='stream_1', stream_name='My Stream')
        add_app(uow=self.uow, app_id='app_3', app_name='My Other App')
        self.uow.apps.session.requests = []

    def teardown_method(self):
        try:
            app = self.app_service.query_one(id='app_1')
            file = PROJECT_ROOT / Path(f'{app.name}.qvf')
            try:
                file.unlink()
            except FileNotFoundError:
                pass
            self.app_service.delete(id='app_1')
            self.app_service.delete(id='app_2')
            self.app_service.delete(id='app_3')
        except AttributeError:
            pass

    def test_get_app_by_name_and_stream(self):
        found_app = self.app_service.get_app_by_name_and_stream_name(app_name='My App', stream_name='My Stream')
        assert 'app_1' == found_app.id

    def test_get_app_by_guid(self):
        found_app = self.app_service.query_one(id='app_2')
        assert 'Not My App' == found_app.name

    def test_get_app_by_name_and_stream_missing(self):
        missing_app = self.app_service.get_app_by_name_and_stream_name(app_name='Another App', stream_name='My Stream')
        assert None is missing_app

    def test_get_app_by_guid_missing(self):
        missing_app = self.app_service.query_one(id='app_4')
        assert None is missing_app

    def test_delete_app(self):
        app = self.app_service.query_one(id='app_1')
        self.app_service.delete(id=app.id)
        get_app_again = self.app_service.query_one(id='app_1')
        assert None is get_app_again
        request = models.QSAPIRequest(
            method='DELETE',
            url=f'/qrs/app/{app.id}'
        )
        assert request in self.uow.apps.session.requests

    def test_reload_app(self):
        app = self.app_service.query_one(id='app_1')
        self.app_service.reload(id=app.id)
        request = models.QSAPIRequest(
            method='POST',
            url=f'/qrs/app/{app.id}/reload'
        )
        assert request in self.uow.apps.session.requests

    def test_copy_app(self):
        app = self.app_service.query_one(id='app_1')
        self.app_service.copy(id=app.id, name=app.name)
        request = models.QSAPIRequest(
            method='POST',
            url=f'/qrs/app/{app.id}/copy',
            params={'name': app.name}
        )
        assert request in self.uow.apps.session.requests

    def test_download_app(self):
        app = self.app_service.query_one(id='app_1')
        self.app_service.download(id=app.id)
        file = PROJECT_ROOT / Path(f'{app.name}.qvf')
        assert isfile(file.absolute())
        for request in self.uow.apps.session.requests:
            if request.method == 'POST':
                url = request.url
                assert f'qrs/app/{app.id}/export' == '/'.join(url.split('/')[1:5])

    def test_publish_app(self):
        app = self.app_service.query_one(id='app_1')
        stream = models.Stream(id='stream_1', name='My Stream')
        self.app_service.publish(id=app.id, stream_id=stream.id)
        request = models.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{app.id}/publish',
            params={'stream': stream.id}
        )
        assert request in self.uow.apps.session.requests

    def test_replace_app(self):
        app = self.app_service.query_one(id='app_1')
        app_to_replace = self.app_service.query_one(id='app_2')
        self.app_service.replace(id=app.id, id_to_replace=app_to_replace.id)
        request = models.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{app.id}/replace',
            params={'app': app_to_replace.id}
        )
        assert request in self.uow.apps.session.requests

    def test_upload_app(self):
        file_name = Path(__file__).absolute()
        app_name = 'My New App'
        self.app_service.upload(file_name=file_name, app_name=app_name)
        for request in self.uow.apps.session.requests:
            if request.method == 'POST':
                assert request.url == '/qrs/app/upload'
                assert request.params == {'name': app_name, 'keepdata': False}
