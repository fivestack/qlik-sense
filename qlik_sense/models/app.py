"""
These are the models and schemas for the Qlik Sense App domain
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

import marshmallow as ma

from qlik_sense.models.stream import StreamCondensed, StreamCondensedSchema
from qlik_sense.models.user import UserCondensed, UserCondensedSchema


@dataclass(unsafe_hash=True)
class AppCondensed:
    """
    Represents a Qlik Sense App with limited attribution

    TODO: add availability_status
    """
    id: str = field(default='', hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    name: str = field(default=None, hash=False)
    app_id: str = field(default=None, hash=False)
    published_timestamp: datetime = field(default=None, hash=False)
    published: bool = field(default=False, hash=False)
    stream: StreamCondensed = field(default=None, hash=False)
    saved_in_product_version: str = field(default=None, hash=False)
    migration_hash: str = field(default=None, hash=False)


@dataclass(unsafe_hash=True)
class App(AppCondensed):
    """
    Represents a Qlik Sense App with full attribution

    TODO: add custom_properties, tags
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_by: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
    owner: UserCondensed = field(default_factory=UserCondensed, hash=False)
    source_app_id: str = field(default=None, hash=False)
    target_app_id: str = field(default=None, hash=False)
    description: str = field(default=None, hash=False)
    file_size: int = field(default=None, hash=False)
    last_reload_time: datetime = field(default=None, hash=False)
    thumbnail: str = field(default=None, hash=False)
    dynamic_color: str = field(default=None, hash=False)


class AppCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense App object with limited attribution
    """
    id = ma.fields.Str(required=True)
    privileges = ma.fields.List(required=False, cls_or_instance=str)
    name = ma.fields.Str(required=False)
    app_id = ma.fields.Str(required=False, data_key='appId')
    published_timestamp = ma.fields.DateTime(required=False, data_key='publishTime')
    published = ma.fields.Bool(required=False)
    stream = ma.fields.Nested(StreamCondensedSchema, required=False)
    saved_in_product_version = ma.fields.Str(required=False)
    migration_hash = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'AppCondensed':
        return AppCondensed(**data)


class AppSchema(AppCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense App object with full attribution
    """
    created_date = ma.fields.DateTime(required=False)
    modified_date = ma.fields.DateTime(required=False)
    modified_by = ma.fields.Str(required=False)
    schema_path = ma.fields.Str(reqeuired=False)
    owner = ma.fields.Nested(UserCondensedSchema, required=True)
    source_app_id = ma.fields.Str(required=False)
    target_app_id = ma.fields.Str(required=False)
    description = ma.fields.Str(required=False)
    file_size = ma.fields.Int(required=False)
    last_reload_time = ma.fields.DateTime(required=False)
    thumbnail = ma.fields.Str(required=False)
    dynamic_color = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'App':
        return App(**data)
