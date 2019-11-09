from tests.test_e2e import config

qs = config.qs


class TestApp:

    def setup_method(self):
        self.test_owner = config.create_test_user()
        self.test_stream = config.create_test_stream()
        self.test_apps = config.create_test_apps()

    def teardown_method(self):
        config.delete_test_apps(test_stream=self.test_stream, test_owner=self.test_owner)
        config.delete_test_stream(self.test_stream)
        config.delete_test_user(self.test_owner)

    def test_query_full(self):
        apps = qs.app.query(filter=f"stream.name eq '{self.test_stream.name}'", full_attribution=True)
        for each_app in apps:
            assert each_app.name is not None

    def test_query_count(self):
        count = qs.app.query_count(filter=f"stream.name eq '{self.test_stream.name}'")
        assert 0 < count

    def test_get_by_name_and_stream(self):
        test_app = self.test_apps[0]
        app_by_name = qs.app.get_by_name_and_stream(app_name=test_app.name, stream_name=self.test_stream.name)
        assert test_app.id == app_by_name.id

    def test_update(self):
        test_app = self.test_apps[0]
        original_name = test_app.name
        test_app.name = 'not_pytest'
        qs.app.update(app=test_app)
        updated_app = qs.app.get_by_name_and_stream(app_name=test_app.name, stream_name=test_app.stream.name)
        assert 'not_pytest' == updated_app.name
        verify_old_app_doesnt_exist = qs.app.get_by_name_and_stream(app_name=original_name,
                                                                    stream_name=test_app.stream.name)
        assert verify_old_app_doesnt_exist is None
