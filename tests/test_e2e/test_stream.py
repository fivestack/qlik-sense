from tests.conftest import stream
from tests.test_e2e import config

qs = config.qs_ssl


class TestStream:

    def setup_method(self):
        self.test_owner = config.create_test_user()
        self.test_stream = config.create_test_stream()

    def teardown_method(self):
        config.delete_test_stream(test_stream=self.test_stream)
        config.delete_test_user(test_user=self.test_owner)

    def test_setup_and_teardown(self):
        assert 1 == 1

    def test_query_full(self):
        streams = qs.stream.query(filter_by=f"name eq '{self.test_stream.name}'", full_attribution=True)
        for each_stream in streams:
            assert each_stream.name is not None

    def test_query_count(self):
        count = qs.stream.query_count(filter_by=f"name eq '{self.test_stream.name}'")
        assert 0 < count

    def test_get_by_name(self):
        stream_by_name = qs.stream.get_by_name(name=self.test_stream.name)
        assert self.test_stream.id == stream_by_name.id

    def test_update(self):
        original_name = self.test_stream.name
        self.test_stream.name = 'not_pytest'
        qs.stream.update(stream=self.test_stream)
        updated_stream = qs.stream.get(id=self.test_stream.id)
        assert 'not_pytest' == updated_stream.name
        verify_old_stream_doesnt_exist = qs.stream.get_by_name(name=original_name)
        assert verify_old_stream_doesnt_exist is None

    def test_create_many(self):
        new_stream1 = stream.Stream(name='pytest1', owner=self.test_owner)
        new_stream2 = stream.Stream(name='pytest2', owner=self.test_owner)
        qs.stream.create_many(streams=[new_stream1, new_stream2])
        self._validate_create_many_and_delete(expected_name=new_stream1.name)
        self._validate_create_many_and_delete(expected_name=new_stream2.name)

    @staticmethod
    def _validate_create_many_and_delete(expected_name: str):
        stream_exists = qs.stream.get_by_name(name=expected_name)
        assert stream_exists
        qs.stream.delete(stream=stream_exists)
        stream_was_deleted = qs.stream.get_by_name(name=expected_name)
        assert stream_was_deleted is None
