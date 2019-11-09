from tests.conftest import SSLClient, user
from tests.test_e2e import auth

qs = SSLClient(scheme=auth.SCHEMA, host=auth.HOST, certificate=auth.CERT)


class TestUser:

    user_name = 'pytest'
    user_directory = 'pytest'
    test_user = None

    def setup_method(self):
        new_user = user.User(user_name=self.user_name,
                             user_directory=self.user_directory,
                             is_blacklisted=False,
                             is_removed_externally=False)
        self.test_user = qs.user.create(user=new_user)
        verify_user_was_created = qs.user.get(id=self.test_user.id)
        assert verify_user_was_created

    def teardown_method(self):
        qs.user.delete(user=self.test_user)
        verify_user_was_deleted = qs.user.get(id=self.test_user.id)
        assert verify_user_was_deleted is None

    def test_query_full(self):
        users = qs.user.query(full_attribution=True)
        for each_user in users:
            assert each_user.name is not None

    def test_query_count(self):
        count = qs.user.query_count(filter_by="userDirectory eq 'INTERNAL'")
        assert 0 < count

    def test_get_by_name_and_directory(self):
        user_by_name = qs.user.get_by_name_and_directory(user_name=self.test_user.user_name,
                                                         directory=self.test_user.user_directory)
        assert self.test_user.id == user_by_name.id

    def test_update(self):
        self.test_user.name = 'not_pytest'
        qs.user.update(user=self.test_user)
        updated_user = qs.user.get(id=self.test_user.id)
        assert 'not_pytest' == updated_user.name

    def test_create_many(self):
        new_user1 = user.User(user_name='pytest1', user_directory=self.user_directory,
                              is_blacklisted=False, is_removed_externally=False)
        new_user2 = user.User(user_name='pytest2', user_directory=self.user_directory,
                              is_blacklisted=False, is_removed_externally=False)
        qs.user.create_many(users=[new_user1, new_user2])
        self._validate_create_many_and_delete(expected_name=new_user1.user_name)
        self._validate_create_many_and_delete(expected_name=new_user2.user_name)

    def _validate_create_many_and_delete(self, expected_name: str):
        user_exists = qs.user.get_by_name_and_directory(user_name=expected_name, directory=self.user_directory)
        assert user_exists
        qs.user.delete(user=user_exists)
        user_was_deleted = qs.user.get_by_name_and_directory(user_name=expected_name, directory=self.user_directory)
        assert user_was_deleted is None
