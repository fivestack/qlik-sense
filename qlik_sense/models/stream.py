from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import marshmallow as ma

from qlik_sense.models.user import UserCondensed, UserCondensedSchema


@dataclass(unsafe_hash=True)
class StreamCondensed:
    """
    Represents a Qlik Sense stream with limited attribution
    """
    id: str = field(default='', hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    name: str = field(default=None, hash=False)


@dataclass(unsafe_hash=True)
class Stream(StreamCondensed):
    """
    Represents a Qlik Sense stream with full attribution

    TODO: add custom_properties, tags
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_by: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
    owner: UserCondensed = field(default_factory=UserCondensed, hash=False)


class StreamCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense Stream object with limited attribution
    """
    id = ma.fields.Str(required=True)
    privileges = ma.fields.List(required=False, cls_or_instance=str)
    name = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'StreamCondensed':
        return StreamCondensed(**data)


class StreamSchema(StreamCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Stream object with full attribution
    """
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_by = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')
    owner = ma.fields.Nested(UserCondensedSchema, required=True)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'Stream':
        return Stream(**data)
