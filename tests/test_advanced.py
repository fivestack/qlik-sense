from .conftest import Client
from . import auth

qs = Client(schema=auth.SCHEMA, host=auth.HOST, port=auth.PORT, user=auth.USER)


def test_get():
    app = qs.app.get_by_name_and_stream(app_name='', stream_name='')
    print('')
    print(app)
    assert 1 == 1
