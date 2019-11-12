from typing import List

from tests.conftest import SSLClient, NTLMClient, user, stream, app
from tests.test_e2e import auth

qs_ssl = SSLClient(scheme=auth.SCHEME,
                   host=auth.HOST,
                   certificate=auth.CERT)
qs_ssl_restricted = SSLClient(scheme=auth.SCHEME,
                              host=auth.HOST,
                              certificate=auth.CERT,
                              user=auth.SAMPLE_USER_NAME,
                              directory=auth.SAMPLE_USER_DIRECTORY)
qs_ntlm = NTLMClient(scheme=auth.SCHEME,
                     host=auth.HOST,
                     domain=auth.SAMPLE_USER_DIRECTORY,
                     username=auth.SAMPLE_USER_NAME,
                     password=auth.SAMPLE_PASSWORD)
qs_sspi = NTLMClient(scheme=auth.SCHEME,
                     host=auth.HOST)


def create_test_user() -> 'user.User':
    user_stub = user.User(user_name=auth.TEST_USER_NAME,
                          user_directory=auth.TEST_USER_DIRECTORY)
    test_user = qs_ssl.user.create(user_stub)
    verify_owner_was_created = qs_ssl.user.get(id=test_user.id)
    assert verify_owner_was_created
    return verify_owner_was_created


def delete_test_user(test_user: 'user.UserCondensed'):
    qs_ssl.user.delete(user=test_user)
    verify_owner_was_deleted = qs_ssl.user.get(id=test_user.id)
    assert verify_owner_was_deleted is None


def create_test_stream() -> 'stream.Stream':
    owner = create_test_user()
    stream_stub = stream.Stream(name='pytest', owner=owner)
    test_stream = qs_ssl.stream.create(stream=stream_stub)
    verify_stream_was_created = qs_ssl.stream.get(id=test_stream.id)
    assert verify_stream_was_created
    return verify_stream_was_created


def delete_test_stream(test_stream: 'stream.StreamCondensed'):
    qs_ssl.stream.delete(stream=test_stream)
    verify_stream_was_deleted = qs_ssl.stream.get(id=test_stream.id)
    assert verify_stream_was_deleted is None


def create_test_apps() -> 'List[app.App]':
    test_apps = []
    for app_name, app_id in auth.TEST_APPS.items():
        source_app = qs_ssl.app.get(id=app_id)
        target_app = qs_ssl.app.copy(app=source_app, name=app_name)
        test_apps.append(target_app)
    return test_apps


def delete_test_apps(test_stream: 'stream.StreamCondensed', test_owner: 'user.UserCondensed'):
    test_apps_by_stream = qs_ssl.app.query(filter_by=f"stream.name eq '{test_stream.name}")
    test_apps_by_owner = qs_ssl.app.query(filter_by=f"owner eq '{test_owner.id}'")
    if isinstance(test_apps_by_stream, list):
        test_apps = test_apps_by_stream.append(test_apps_by_owner)
    else:
        test_apps = test_apps_by_owner
    if test_apps:
        for test_app in test_apps:
            qs_ssl.app.delete(app=test_app)
