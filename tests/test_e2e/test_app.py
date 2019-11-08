from tests.conftest import SSLClient, stream
from tests.test_e2e import auth

qs = SSLClient(scheme=auth.SCHEMA, host=auth.HOST, certificate=auth.CERT)


def get_app_by_name_and_stream(app_name: str, stream_name: str, full_attribution: bool = False):
    apps = qs.app.get_by_name_and_stream(app_name=app_name, stream_name=stream_name, full_attribution=full_attribution)
    if apps:
        return apps[0]
    return


def test_query_full():
    apps = qs.app.query(full_attribution=True)
    for each_app in apps:
        assert each_app.name is not None


def test_app_count():
    count = qs.app.query_count()
    assert 0 < count


class TestApp:

    stream_name = 'pytest'

    def setup_method(self):
        owner = qs.user.get_by_name_and_directory(user_name=auth.USER_NAME, directory=auth.USER_DIRECTORY)
        test_stream = stream.Stream(name=self.stream_name, owner=owner)
        qs.stream.create(stream=test_stream)
        # copy app(s) into stream

    def teardown_method(self):
        test_streams = qs.stream.get_by_name(name=self.stream_name)
        for test_stream in test_streams:
            test_apps = qs.app.query(filter_by=f"stream.name eq '{self.stream_name}")
            for test_app in test_apps:
                qs.app.delete(app=test_app)
            qs.stream.delete(stream=test_stream)

    def test_get_by_name_and_stream(self):
        app_name = 'test app'
        apps = qs.app.get_by_name_and_stream(app_name=app_name, stream_name=self.stream_name)
        for app in apps:
            assert app_name == app.name
            assert self.stream_name == app.stream.name
