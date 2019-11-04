from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import marshmallow as ma

from .user import UserCondensed, UserCondensedSchema
from .tag import TagCondensedSchema, TagCondensed
from .custom_property import CustomPropertyValueSchema, CustomPropertyValue


@dataclass(unsafe_hash=True)
class StreamCondensed:
    """
    Represents a Qlik Sense Stream with limited attribution
    """
    id: str = field(default=None, hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    name: str = field(default=None, hash=False)


@dataclass(unsafe_hash=True)
class Stream(StreamCondensed):
    """
    Represents a Qlik Sense Stream with full attribution
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_user: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
    custom_properties: List[CustomPropertyValue] = field(default_factory=list, hash=False)
    owner: UserCondensed = field(default_factory=UserCondensed, hash=False)
    tags: List[TagCondensed] = field(default_factory=list, hash=False)


class StreamCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense Stream object with limited attribution
    """
    id = ma.fields.UUID(required=False)
    privileges = ma.fields.List(cls_or_instance=str, required=False)
    name = ma.fields.Str(required=True)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'StreamCondensed':
        return StreamCondensed(**data)


class StreamSchema(StreamCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Stream object with full attribution
    """
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_user = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')
    custom_properties = ma.fields.Nested(nested=CustomPropertyValueSchema, many=True, required=False,
                                         data_key='customProperties')
    owner = ma.fields.Nested(UserCondensedSchema, many=False, required=True)
    tags = ma.fields.Nested(TagCondensedSchema, many=True, required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'Stream':
        return Stream(**data)
