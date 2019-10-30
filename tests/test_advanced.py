import pytest

from .conftest import api
from . import auth


def test_reload():
    qs = api.QlikSense(host=auth.HOST, certificate=auth.CERTIFICATE)
    app = qs.get_app_by_name_and_stream('Test', 'Everyone')
    qs.reload_app(app)
    assert 1 == 1
