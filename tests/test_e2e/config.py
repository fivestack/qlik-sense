from typing import List

from tests.conftest import SSLClient, user, stream, app
from tests.test_e2e import auth

qs = SSLClient(scheme=auth.SCHEMA, host=auth.HOST, certificate=auth.CERT)


def create_test_user() -> 'user.User':
    user_stub = user.User(user_name='pytest',
                          user_directory='pytest')
    test_user = qs.user.create(user_stub)
    verify_owner_was_created = qs.user.get(id=test_user.id)
    assert verify_owner_was_created
    return verify_owner_was_created


def delete_test_user(test_user: 'user.UserCondensed'):
    qs.user.delete(user=test_user)
    verify_owner_was_deleted = qs.user.get(id=test_user.id)
    assert verify_owner_was_deleted is None


def create_test_stream() -> 'stream.Stream':
    owner = create_test_user()
    stream_stub = stream.Stream(name='pytest', owner=owner)
    test_stream = qs.stream.create(stream=stream_stub)
    verify_stream_was_created = qs.stream.get(id=test_stream.id)
    assert verify_stream_was_created
    return verify_stream_was_created


def delete_test_stream(test_stream: 'stream.StreamCondensed'):
    qs.stream.delete(stream=test_stream)
    verify_stream_was_deleted = qs.stream.get(id=test_stream.id)
    assert verify_stream_was_deleted is None


def create_test_apps() -> 'List[app.App]':
    app_suffix = 1
    test_apps = []
    for test_app in auth.TEST_APPS:
        app_name = test_app['app_name']
        stream_name = test_app['stream_name']
        source_app = qs.app.get_by_name_and_stream(app_name=app_name, stream_name=stream_name)
        target_app = qs.app.copy(app=source_app, name=f'pytest_{app_suffix}')
        test_apps.append(target_app)
        app_suffix += 1
    return test_apps


def delete_test_apps(test_stream: 'stream.StreamCondensed', test_owner: 'user.UserCondensed'):
    test_apps = qs.app.query(filter_by=f"stream.name eq '{test_stream.name}")
    test_apps.append(qs.app.query(filter_by=f"owner.userId eq '{test_owner.user_name}' and "
                                            f"owner.userDirectory eq '{test_owner.user_directory}'"))
    for test_app in test_apps:
        qs.app.delete(app=test_app)
