from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import marshmallow as ma

from .tag import TagCondensedSchema, TagCondensed
from .custom_property import CustomPropertyValueSchema, CustomPropertyValue


@dataclass(unsafe_hash=True)
class UserCondensed:
    """
    Represents a Qlik Sense User with limited attribution
    """
    id: str = field(default=None, hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    user_id: str = field(default=None, hash=True)
    user_directory: str = field(default=None, hash=True)
    name: str = field(default=None, hash=False)


@dataclass(unsafe_hash=True)
class UserAttribute:
    """
    Represents a Qlik Sense User Attribute
    """
    id: str = field(default=None, hash=True)
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_user: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
    attribute_type: str = field(default=None, hash=True)
    attribute_value: str = field(default=None, hash=False)
    external_id: str = field(default=None, hash=False)


@dataclass(unsafe_hash=True)
class User(UserCondensed):
    """
    Represents a Qlik Sense User with full attribution
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_user: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
    custom_properties: List[CustomPropertyValue] = field(default_factory=list, hash=False)
    roles: List[str] = field(default_factory=list, hash=False)
    attributes: List[UserAttribute] = field(default_factory=list, hash=False)
    is_inactive: bool = field(default_factory=False, hash=False)
    is_removed_externally: bool = field(default=False, hash=False)
    is_blacklisted: bool = field(default=False, hash=False)
    delete_is_prohibited: bool = field(default=False, hash=False)
    tags: List[TagCondensed] = field(default_factory=list, hash=False)


class UserCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense User object with limited attribution
    """
    id = ma.fields.UUID(required=False)
    privileges = ma.fields.List(cls_or_instance=str, required=False)
    user_id: str = ma.fields.Str(required=True, data_key='userId')
    user_directory: str = ma.fields.Str(required=True, data_key='userDirectory')
    name: str = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'UserCondensed':
        return UserCondensed(**data)


class UserAttributeSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense User Attribute object
    """
    id = ma.fields.UUID(required=False)
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_user = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')
    attribute_type = ma.fields.Str(required=True, data_key='attributeType')
    attribute_value = ma.fields.Str(required=False, data_key='attributeValue')
    external_id = ma.fields.Str(required=False, data_key='externalId')

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'UserAttribute':
        return UserAttribute(**data)


class UserSchema(UserCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense User object with full attribution
    """
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_user = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')
    custom_properties = ma.fields.Nested(nested=CustomPropertyValueSchema, many=True, required=False,
                                         data_key='customProperties')
    roles = ma.fields.List(cls_or_instance=str, required=False)
    attributes = ma.fields.Nested(UserAttributeSchema, many=True, required=False)
    is_inactive = ma.fields.Bool(required=False, data_key='inactive')
    is_removed_externally = ma.fields.Bool(required=True, data_key='removedExternally')
    is_blacklisted = ma.fields.Bool(required=True, data_key='blacklisted')
    delete_is_prohibited = ma.fields.Bool(required=False, data_key='deleteProhibited')
    tags = ma.fields.Nested(TagCondensedSchema, many=True, required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'User':
        return User(**data)
