from tests.conftest import SSLClient, stream, user
from tests.test_e2e import auth

qs = SSLClient(scheme=auth.SCHEMA, host=auth.HOST, certificate=auth.CERT)


class TestApp:

    stream_name = 'pytest'
    test_owner = None
    test_stream = None

    def setup_method(self):
        owner = user.User(user_name=auth.TEST_USER_NAME, user_directory=auth.TEST_USER_DIRECTORY)
        self.test_owner = qs.user.create(owner)
        verify_owner_was_created = qs.user.get(id=self.test_owner.id)
        assert verify_owner_was_created
        test_stream = stream.Stream(name=self.stream_name, owner=self.test_owner)
        self.test_stream = qs.stream.create(stream=test_stream)
        verify_stream_was_created = qs.stream.get(id=self.test_stream.id)
        assert verify_stream_was_created
        # copy app(s) into stream
        # change ownership of app(s) to test_owner

    def teardown_method(self):
        test_apps = qs.app.query(filter_by=f"stream.name eq '{self.test_stream.name}")
        test_apps.append(qs.app.query(filter_by=f"userId eq '{self.test_owner.user_name}' and "
                                                f"userDirectory eq '{self.test_owner.user_directory}'"))
        for test_app in test_apps:
            qs.app.delete(app=test_app)
        qs.stream.delete(stream=self.test_stream)
        qs.user.delete(user=self.test_owner)

    def test_query_full(self):
        apps = qs.app.query(full_attribution=True)
        for each_app in apps:
            assert each_app.name is not None

    def test_app_count(self):
        count = qs.app.query_count()
        assert 0 < count

    def test_get_by_name_and_stream(self):
        app_name = 'test app'
        apps = qs.app.get_by_name_and_stream(app_name=app_name, stream_name=self.stream_name)
        for app in apps:
            assert app_name == app.name
            assert self.stream_name == app.stream.name
