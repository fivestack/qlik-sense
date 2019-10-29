import pytest

from .conftest import api


@pytest.skip
def test_reload():
    qs = api.QlikSense(host='', certificate='')
    app = qs.get_app_by_name_and_stream('Test', 'Everyone')
    qs.reload_app(app)
    assert 1 == 1
