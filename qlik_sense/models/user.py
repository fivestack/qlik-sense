from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import marshmallow as ma


@dataclass(unsafe_hash=True)
class UserCondensed:
    """
    Represents a Qlik Sense user with limited attribution
    """
    id: str = field(default='', hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    user_id: str = field(default='', hash=True)
    user_directory: str = field(default='', hash=True)
    name: str = field(default=None, hash=False)


@dataclass(unsafe_hash=True)
class User(UserCondensed):
    """
    Represents a Qlik Sense user with full attribution

    TODO: add custom_properties, attributes, tags
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_by: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
    roles: List[str] = field(default_factory=list, hash=False)
    inactive: bool = field(default_factory=False, hash=False)
    removed_externally: bool = field(default=False, hash=False)
    blacklisted: bool = field(default=False, hash=False)
    delete_prohibited: bool = field(default=False, hash=False)


class UserCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense User object with limited attribution
    """
    id = ma.fields.Str(required=True)
    privileges = ma.fields.List(required=False, cls_or_instance=str)
    user_id: str = ma.fields.Str(required=True, data_key='userId')
    user_directory: str = ma.fields.Str(required=True, data_key='userDirectory')
    name: str = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'UserCondensed':
        return UserCondensed(**data)


class UserSchema(UserCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense User object with full attribution
    """
    created_date = ma.fields.DateTime(required=False)
    modified_date = ma.fields.DateTime(required=False)
    modified_by = ma.fields.Str(required=False)
    schema_path = ma.fields.Str(required=False)
    roles = ma.fields.List(cls_or_instance=str, hash=False)
    inactive = ma.fields.Bool(required=False)
    removed_externally = ma.fields.Bool(required=False)
    blacklisted = ma.fields.Bool(required=False)
    delete_prohibited = ma.fields.Bool(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'User':
        return User(**data)
