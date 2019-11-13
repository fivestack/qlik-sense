from typing import TYPE_CHECKING
import json
from dataclasses import asdict

from .conftest import app, stream, util
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
        self.client.app.query(filter_by=query_string)
        request = util.QSAPIRequest(
            method='GET',
            url=f'/qrs/app',
            params={
                'filter': query_string,
                'orderby': None,
                'privileges': None
            },
            data=None
        )
        assert request in self.client.app.requests

    def test_query_count(self):
        pass

    def test_get_by_name_and_stream(self):
        self.client.app.get_by_name_and_stream(app_name='My App', stream_name='My Stream')
        request = util.QSAPIRequest(
            method='GET',
            url=f'/qrs/app',
            params={
                'filter': "name eq 'My App' and stream.name eq 'My Stream'",
                'orderby': None,
                'privileges': None
            }
        )
        assert request in self.client.app.requests

    def test_get(self):
        self.client.app.get(id='app_2')
        request = util.QSAPIRequest(
            method='GET',
            url=f'/qrs/app/app_2',
            params={'privileges': None},
            data=None
        )
        assert request in self.client.app.requests

    def test_update(self):
        test_app = self.client.app.get_fake_app(id='app_1')
        self.client.app.update(app=test_app)
        request = util.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{test_app.id}',
            params={'privileges': None},
            data=json.dumps(asdict(test_app))
        )
        assert request in self.client.app.requests

    def test_delete(self):
        test_app = self.client.app.get_fake_app(id='app_1')
        self.client.app.delete(app=test_app)
        request = util.QSAPIRequest(
            method='DELETE',
            url=f'/qrs/app/{test_app.id}'
        )
        assert request in self.client.app.requests

    def test_copy(self):
        test_app = self.client.app.get_fake_app(id='app_1')
        self.client.app.copy(app=test_app, name=test_app.name)
        request = util.QSAPIRequest(
            method='POST',
            url=f'/qrs/app/{test_app.id}/copy',
            params={
                'name': test_app.name,
                'includecustomproperties': False
            },
            data=None
        )
        assert request in self.client.app.requests

    def test_replace(self):
        test_app = self.client.app.get_fake_app(id='app_1')
        app_to_replace = self.client.app.get_fake_app(id='app_2')
        self.client.app.replace(app=test_app, app_to_replace=app_to_replace)
        request = util.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{test_app.id}/replace',
            params={'app': app_to_replace.id}
        )
        assert request in self.client.app.requests

    def test_reload(self):
        test_app = self.client.app.get_fake_app(id='app_1')
        self.client.app.reload(app=test_app)
        request = util.QSAPIRequest(
            method='POST',
            url=f'/qrs/app/{test_app.id}/reload'
        )
        assert request in self.client.app.requests

    def test_publish(self):
        test_app = self.client.app.get_fake_app(id='app_1')
        test_stream = stream.Stream(id='stream_1', name='My Stream')
        self.client.app.publish(app=test_app, stream=test_stream)
        request = util.QSAPIRequest(
            method='PUT',
            url=f'/qrs/app/{test_app.id}/publish',
            params={
                'stream': test_stream.id,
                'name': test_app.name
            },
            data=None
        )
        assert request in self.client.app.requests

    def test_unpublish(self):
        pass

    def test_get_export_token(self):
        pass

    def test_create_export(self):
        test_app = self.client.app.get_fake_app(id='app_1')
        self.client.app.create_export(app=test_app)
        for request in self.client.app.requests:
            if request.method == 'POST':
                url = request.url
                assert ['qrs', 'app', test_app.id, 'export'] == url.split('/')[1:5]

    def test_delete_export(self):
        pass

    def test_download_file(self):
        app_export = app.AppExport(schema_path='',
                                   export_token='',
                                   app_id='app_1',
                                   download_path='path/to/my/download',
                                   is_cancelled=False)
        self.client.app.download_file(app_export=app_export)
        request = util.QSAPIRequest(
            method='GET',
            url=f'/qrs/app/{app_export.download_path}'
        )
        assert request in self.client.app.requests
