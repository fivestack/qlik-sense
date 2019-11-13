from dataclasses import dataclass, field, asdict
from typing import List, Union

import marshmallow as ma

from .base import EntityCondensedSchema, EntityCondensed, EntitySchema, Entity, AuditingSchema, Auditing
from .tag import TagCondensedSchema, TagCondensed
from .custom_property import CustomPropertyValueSchema, CustomPropertyValue


@dataclass(unsafe_hash=True)
class UserCondensed(EntityCondensed):
    """
    Represents a Qlik Sense User with limited attribution
    """
    user_name: str = field(default=None, hash=True)
    user_directory: str = field(default=None, hash=True)


class UserCondensedSchema(EntityCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense User object with limited attribution
    """
    user_name: str = ma.fields.Str(required=True, data_key='userId')
    user_directory: str = ma.fields.Str(required=True, data_key='userDirectory')

    @ma.pre_dump()
    def pre_dump(self, data: 'Union[UserCondensed, dict]', **kwargs) -> dict:
        if isinstance(data, UserCondensed):
            return asdict(data)
        return data

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'UserCondensed':
        return UserCondensed(**data)


@dataclass(unsafe_hash=True)
class UserAttribute(Auditing):
    """
    Represents a Qlik Sense User Attribute
    """
    id: str = field(default=None, hash=True)
    attribute_type: str = field(default=None, hash=True)
    attribute_value: str = field(default=None, hash=False)
    external_id: str = field(default=None, hash=False)


class UserAttributeSchema(AuditingSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense User Attribute object
    """
    id = ma.fields.UUID(required=False)
    attribute_type = ma.fields.Str(required=True, data_key='attributeType')
    attribute_value = ma.fields.Str(required=False, data_key='attributeValue')
    external_id = ma.fields.Str(required=False, data_key='externalId')

    @ma.pre_dump()
    def pre_dump(self, data: 'Union[UserAttribute, dict]', **kwargs) -> dict:
        if isinstance(data, UserAttribute):
            return asdict(data)
        return data

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'UserAttribute':
        return UserAttribute(**data)


@dataclass(unsafe_hash=True)
class User(UserCondensed, Entity):
    """
    Represents a Qlik Sense User with full attribution
    """
    custom_properties: List[CustomPropertyValue] = field(default_factory=list, hash=False)
    roles: List[str] = field(default_factory=list, hash=False)
    attributes: List[UserAttribute] = field(default_factory=list, hash=False)
    is_inactive: bool = field(default=False, hash=False)
    is_removed_externally: bool = field(default=False, hash=False)
    is_blacklisted: bool = field(default=False, hash=False)
    delete_is_prohibited: bool = field(default=False, hash=False)
    tags: List[TagCondensed] = field(default_factory=list, hash=False)


class UserSchema(UserCondensedSchema, EntitySchema):
    """
    A marshmallow schema corresponding to a Qlik Sense User object with full attribution
    """
    custom_properties = ma.fields.Nested(nested=CustomPropertyValueSchema, many=True, required=False,
                                         data_key='customProperties')
    roles = ma.fields.List(cls_or_instance=ma.fields.Str, required=False, allow_none=True)
    attributes = ma.fields.Nested(UserAttributeSchema, many=True, required=False)
    is_inactive = ma.fields.Bool(required=False, data_key='inactive')
    is_removed_externally = ma.fields.Bool(required=True, data_key='removedExternally')
    is_blacklisted = ma.fields.Bool(required=True, data_key='blacklisted')
    delete_is_prohibited = ma.fields.Bool(required=False, data_key='deleteProhibited')
    tags = ma.fields.Nested(TagCondensedSchema, many=True, required=False)

    @ma.pre_dump()
    def pre_dump(self, data: 'Union[User, dict]', **kwargs) -> dict:
        if isinstance(data, User):
            return asdict(data)
        return data

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'User':
        return User(**data)
