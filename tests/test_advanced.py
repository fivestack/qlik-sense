import pytest

from .conftest import Client
from . import auth


def test_get():
    qs = Client(host=auth.HOST, user=auth.USER)
    app = qs.app.get_app_by_name_and_stream('', '')
    print('')
    print(app)
    assert 1 == 1
