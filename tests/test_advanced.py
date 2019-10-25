import pytest

from .conftest import api


@pytest.fixture
def qs():
    return api.QlikSense(host='', certificate='')


def test_reload(qs):
    guid = qs.search_for_guid_by_name('Test', 'Everyone')
    qs.reload(guid)
    assert 1 == 1
