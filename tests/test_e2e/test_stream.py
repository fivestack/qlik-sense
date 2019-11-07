from tests.conftest import SSLClient, stream, user
from tests.test_e2e import auth

qs = SSLClient(scheme=auth.SCHEMA, host=auth.HOST, certificate=auth.CERT)


def get_stream_by_name(name: str, full_attribution: bool = False):
    streams = qs.stream.get_by_name(name=name, full_attribution=full_attribution)
    if streams:
        return streams[0]
    return


def test_query_full():
    streams = qs.stream.query(full_attribution=True)
    for each_stream in streams:
        assert each_stream.name is not None


def test_query_count():
    count = qs.stream.query_count()
    assert 0 < count


def test_get_by_name():
    stream_name = 'Data Security Testing'
    streams = qs.stream.get_by_name(name=stream_name)
    for each_stream in streams:
        assert stream_name == each_stream.name


def test_get():
    test_stream = get_stream_by_name('Data Security Testing')
    actual_stream = qs.stream.get(id=test_stream.id)
    assert test_stream.name == actual_stream.name


def test_create_and_delete():
    new_user = user.User(user_name='pytest', user_directory='pytest', is_blacklisted=False, is_removed_externally=False)
    qs.user.create(user=new_user)
    owner = qs.user.get_by_name_and_directory(user_name='pytest', directory='pytest')
    new_stream = stream.Stream(name='pytest', owner=owner[0])
    qs.stream.create(stream=new_stream)
    found_stream = get_stream_by_name(name='pytest')
    assert 'pytest' == found_stream.name.lower()
    qs.stream.delete(stream=found_stream)
    missing_stream = get_stream_by_name(name='pytest')
    assert missing_stream is None
    qs.user.delete(user=owner)


def test_create_many():
    new_user = user.User(user_name='pytest', user_directory='pytest', is_blacklisted=False, is_removed_externally=False)
    qs.user.create(user=new_user)
    owner = qs.user.get_by_name_and_directory(user_name='pytest', directory='pytest')
    new_stream1 = stream.Stream(name='pytest1', owner=owner[0])
    new_stream2 = stream.Stream(name='pytest2', owner=owner[0])
    qs.stream.create_many(streams=[new_stream1, new_stream2])
    found_stream1 = get_stream_by_name(name='pytest1')
    assert 'pytest1' == found_stream1.name.lower()
    found_stream2 = get_stream_by_name(name='pytest2')
    assert 'pytest2' == found_stream2.name.lower()
    qs.stream.delete(stream=found_stream1)
    qs.stream.delete(stream=found_stream2)
    missing_stream1 = get_stream_by_name(name='pytest1')
    assert missing_stream1 is None
    missing_stream2 = get_stream_by_name(name='pytest2')
    assert missing_stream2 is None
    qs.user.delete(user=owner)


def test_update():
    new_user = user.User(user_name='pytest', user_directory='pytest', is_blacklisted=False, is_removed_externally=False)
    qs.user.create(user=new_user)
    owner = qs.user.get_by_name_and_directory(user_name='pytest', directory='pytest')
    new_stream = stream.Stream(name='pytest', owner=owner[0])
    qs.stream.create(stream=new_stream)
    found_stream = get_stream_by_name(name='pytest', full_attribution=True)
    assert 'pytest' == found_stream.name
    found_stream.name = 'not_pytest'
    qs.stream.update(stream=found_stream)
    missing_stream = get_stream_by_name(name='pytest')
    assert missing_stream is None
    updated_stream = get_stream_by_name(name='not_pytest')
    assert 'not_pytest' == updated_stream.name
    qs.user.delete(user=owner)
