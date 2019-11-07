from tests.conftest import SSLClient, user
from tests.test_e2e import auth


qs = SSLClient(scheme=auth.SCHEMA, host=auth.HOST, certificate=auth.CERT)


def get_user_by_name_and_directory(user_name: str = 'sa_repository',
                                   directory: str = 'INTERNAL',
                                   full_attribution: bool = False):
    users = qs.user.get_by_name_and_directory(user_name=user_name,
                                              directory=directory,
                                              full_attribution=full_attribution)
    if users:
        return users[0]
    return


def delete_user_by_name_and_directory(user_name: str, directory: str):
    users = qs.user.get_by_name_and_directory(user_name=user_name, directory=directory)
    if users:
        for each_user in users:
            qs.user.delete(user=each_user)
    return


def test_query_full():
    users = qs.user.query(full_attribution=True)
    for each_user in users:
        assert each_user.name is not None


def test_query_count():
    count = qs.user.query_count(filter_by="userDirectory eq 'INTERNAL'")
    assert 0 < count


def test_get_by_name_and_directory():
    user_name = 'sa_repository'
    directory = 'INTERNAL'
    users = qs.user.get_by_name_and_directory(user_name=user_name, directory=directory)
    for each_user in users:
        assert user_name == each_user.user_name
        assert directory == each_user.user_directory


def test_get():
    test_user = get_user_by_name_and_directory()
    actual_user = qs.user.get(id=test_user.id)
    assert test_user.user_name == actual_user.user_name
    assert test_user.user_directory == actual_user.user_directory


def test_create_and_delete():
    new_user = user.User(user_name='pytest', user_directory='pytest', is_blacklisted=False, is_removed_externally=False)
    qs.user.create(user=new_user)
    found_user = get_user_by_name_and_directory(user_name='pytest', directory='pytest')
    assert 'pytest' == found_user.user_name.lower()
    assert 'pytest' == found_user.user_directory.lower()
    qs.user.delete(user=found_user)
    missing_user = get_user_by_name_and_directory(user_name='pytest', directory='pytest')
    assert missing_user is None


def test_create_many():
    new_user1 = user.User(user_name='pytest1', user_directory='pytest', is_blacklisted=False, is_removed_externally=False)
    new_user2 = user.User(user_name='pytest2', user_directory='pytest', is_blacklisted=False, is_removed_externally=False)
    qs.user.create_many(users=[new_user1, new_user2])
    found_user1 = get_user_by_name_and_directory(user_name='pytest1', directory='pytest')
    assert 'pytest1' == found_user1.user_name.lower()
    assert 'pytest' == found_user1.user_directory.lower()
    found_user2 = get_user_by_name_and_directory(user_name='pytest2', directory='pytest')
    assert 'pytest2' == found_user2.user_name.lower()
    assert 'pytest' == found_user2.user_directory.lower()
    qs.user.delete(user=found_user1)
    qs.user.delete(user=found_user2)
    missing_user1 = get_user_by_name_and_directory(user_name='pytest1', directory='pytest')
    assert missing_user1 is None
    missing_user2 = get_user_by_name_and_directory(user_name='pytest2', directory='pytest')
    assert missing_user2 is None


def test_update():
    new_user = user.User(user_name='pytest', user_directory='pytest', is_blacklisted=False, is_removed_externally=False)
    qs.user.create(user=new_user)
    found_user = get_user_by_name_and_directory(user_name='pytest', directory='pytest', full_attribution=True)
    assert None is found_user.name
    found_user.name = 'not_pytest'
    qs.user.update(user=found_user)
    updated_user = get_user_by_name_and_directory(user_name='pytest', directory='pytest')
    assert 'not_pytest' == updated_user.name
