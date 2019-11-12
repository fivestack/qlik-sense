from datetime import datetime
import uuid

from tests.test_e2e import config

qs = config.qs_ssl


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

    def test_replace(self):
        source_app = self.test_apps[0]
        app_to_replace = self.test_apps[1]
        replaced_app = qs.app.replace(app=source_app, app_to_replace=app_to_replace)
        assert app_to_replace.id == replaced_app.id
        assert source_app.name == replaced_app.name

    def test_reload(self):
        test_app = self.test_apps[0]
        now = datetime.now()
        qs.app.reload(test_app)
        reloaded_app = qs.app.get(id=test_app.id)
        assert now < reloaded_app.last_reload_time

    def test_publish(self):
        unpublished_apps = [app for app in self.test_apps if not app.is_published]
        if len(unpublished_apps) == 0:
            test_app = qs.app.unpublish(app=self.test_apps[0])
        else:
            test_app = unpublished_apps[0]
        published_app = qs.app.publish(app=test_app,
                                       stream=self.test_stream,
                                       name='pytest_published')
        assert test_app.id == published_app.id
        assert 'pytest_published' == published_app.name
        assert published_app.is_published
        assert self.test_stream.name == published_app.stream.name

    def test_unpublish(self):
        published_apps = [app for app in self.test_apps if app.is_published]
        if len(published_apps) == 0:
            test_app = qs.app.publish(app=self.test_apps[0], stream=self.test_stream)
        else:
            test_app = published_apps[0]
        unpublished_app = qs.app.unpublish(app=test_app)
        assert test_app.id == unpublished_app.id
        assert not unpublished_app.is_published
        assert None is unpublished_app.stream

    def test_get_export_token(self):
        test_app = self.test_apps[0]
        export_token = qs.app.get_export_token(app=test_app)
        sample_token = uuid.uuid4()
        assert isinstance(export_token, str)
        assert len(str(sample_token)) == len(export_token)

    def test_create_export(self):
        test_app = self.test_apps[0]
        app_export = qs.app.create_export(app=test_app)
        assert test_app.id == app_export.app_id
        assert not app_export.is_cancelled
        assert 0 < len(app_export.download_path)

    def test_delete_export(self):
        test_app = self.test_apps[0]
        app_export = qs.app.create_export(app=test_app)
        cancelled_app_export = qs.app.delete_export(app_export=app_export)
        assert test_app.id == cancelled_app_export.app_id
        assert app_export.is_cancelled
