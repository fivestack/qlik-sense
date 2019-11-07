from tests.conftest import SSLClient
from tests.test_e2e import auth

qs = SSLClient(scheme=auth.SCHEMA, host=auth.HOST, certificate=auth.CERT)


def test_get_by_name_and_stream():
    app_name = ''
    stream_name = 'Data Security Testing'
    apps = qs.app.get_by_name_and_stream(app_name=app_name, stream_name=stream_name)
    for app in apps:
        assert app_name == app.name
        assert stream_name == app.stream.name
