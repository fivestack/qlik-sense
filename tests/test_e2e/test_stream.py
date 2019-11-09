from tests.conftest import SSLClient, stream, user
from tests.test_e2e import auth

qs = SSLClient(scheme=auth.SCHEMA, host=auth.HOST, certificate=auth.CERT)


class TestStream:

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

    def teardown_method(self):
        qs.stream.delete(stream=self.test_stream)
        verify_stream_was_deleted = qs.stream.get(id=self.test_stream.id)
        assert verify_stream_was_deleted is None
        qs.user.delete(user=self.test_owner)
        verify_owner_was_deleted = qs.user.get(id=self.test_owner.id)
        assert verify_owner_was_deleted is None

    def test_query_full(self):
        streams = qs.stream.query(full_attribution=True)
        for each_stream in streams:
            assert each_stream.name is not None

    def test_query_count(self):
        count = qs.stream.query_count(filter_by=f"name eq '{self.stream_name}'")
        assert 0 < count

    def test_get_by_name(self):
        stream_by_name = qs.stream.get_by_name(name=self.test_stream.name)
        assert self.test_stream.id == stream_by_name.id

    def test_update(self):
        self.test_stream.name = 'not_pytest'
        qs.stream.update(stream=self.test_stream)
        updated_stream = qs.stream.get(id=self.test_stream.id)
        assert 'not_pytest' == updated_stream.name
        verify_old_stream_doesnt_exist = qs.stream.get_by_name(name=self.stream_name)
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
