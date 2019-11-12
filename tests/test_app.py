from typing import TYPE_CHECKING

import qlik_sense.services.base
import qlik_sense.services.util
import qlik_sense.models.stream
from .fakes import FakeAppService

if TYPE_CHECKING:
    from .conftest import Client

fake_apps = [
    {'app_id': 'app_1', 'app_name': 'My App', 'stream_id': 'stream_1', 'stream_name': 'My Stream'},
    {'app_id': 'app_2', 'app_name': 'Not My App', 'stream_id': 'stream_1', 'stream_name': 'My Stream'},
    {'app_id': 'app_3', 'app_name': 'My Other App'}
]


def client_factory() -> 'Client':
    app_service = FakeAppService()
    for app in fake_apps:
        app_service.add_fake_app(**app)
    return app_service.client


class TestApp:

    def setup_method(self):
        self.client = client_factory()

    def test_query(self):
        query_string = 'find my app'
        self.client.app.query(query_string=query_string)
        request = qlik_sense.services.util.QSAPIRequest(
            method='GET',
            url=f'/qrs/app',
            params={'filter': query_string}
        )
        assert request in self.client.app.requests

    def test_query_count(self):
        pass

    def test_get_by_name_and_stream(self):
        self.client.app.get_by_name_and_stream(app_name='My App', stream_name='My Stream')
        request = qlik_sense.services.util.QSAPIRequest(
            method='GET',
            url=f'/qrs/app',
            params={'filter': "name eq 'My App' and stream.name eq 'My Stream'"}
        )
        assert request in self.client.app.requests

    def test_get(self):
        self.client.app.get(id='app_2')
        request = qlik_sense.services.util.QSAPIRequest(
            method='GET',
            url=f'/qrs/app/app_2'
        )
        assert request in self.client.app.requests

    def test_update(self):
        app = self.client.app.get_fake_app(id='app_1')
        self.client.app.update(app=app)
        request = app.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{app.id}'
        )
        assert request in self.client.app.requests

    def test_delete(self):
        app = self.client.app.get_fake_app(id='app_1')
        self.client.app.delete(app=app)
        request = app.QSAPIRequest(
            method='DELETE',
            url=f'/qrs/app/{app.id}'
        )
        assert request in self.client.app.requests

    def test_copy(self):
        app = self.client.app.get_fake_app(id='app_1')
        self.client.app.copy(app=app, name=app.name)
        request = app.QSAPIRequest(
            method='POST',
            url=f'/qrs/app/{app.id}/copy',
            params={'name': app.name}
        )
        assert request in self.client.app.requests

    def test_replace(self):
        app = self.client.app.get_fake_app(id='app_1')
        app_to_replace = self.client.app.get_fake_app(id='app_2')
        self.client.app.replace(app=app, app_to_replace=app_to_replace)
        request = app.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{app.id}/replace',
            params={'app': app_to_replace.id}
        )
        assert request in self.client.app.requests

    def test_reload(self):
        app = self.client.app.get_fake_app(id='app_1')
        self.client.app.reload(app=app)
        request = app.QSAPIRequest(
            method='POST',
            url=f'/qrs/app/{app.id}/reload'
        )
        assert request in self.client.app.requests

    def test_publish(self):
        app = self.client.app.get_fake_app(id='app_1')
        stream = qlik_sense.models.stream.Stream(id='stream_1', name='My Stream')
        self.client.app.publish(app=app, stream=stream)
        request = app.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{app.id}/publish',
            params={'stream': stream.id}
        )
        assert request in self.client.app.requests

    def test_unpublish(self):
        pass

    def test_get_export_token(self):
        pass

    def test_create_export(self):
        app = self.client.app.get_fake_app(id='app_1')
        self.client.app.create_export(app=app)
        for request in self.client.app.requests:
            if request.method == 'POST':
                url = request.url
                assert ['qrs', 'app', app.id, 'export'] == url.split('/')[1:5]

    def test_delete_export(self):
        pass

    def test_download_file(self):
        url = 'path/to/my/download'
        self.client.app.download_file(url=url)
        request = qlik_sense.services.util.QSAPIRequest(
            method='GET',
            url=f'/qrs/app/{url}'
        )
        assert request in self.client.app.requests
