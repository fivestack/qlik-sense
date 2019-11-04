"""
These are the models and schemas for the Qlik Sense App domain
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

import marshmallow as ma

from .base import EntityCondensedSchema, EntityCondensed, EntitySchema, Entity
from .stream import StreamCondensed, StreamCondensedSchema
from .user import UserCondensed, UserCondensedSchema
from .tag import TagCondensedSchema, TagCondensed
from .custom_property import CustomPropertyValueSchema, CustomPropertyValue


@dataclass(unsafe_hash=True)
class AppCondensed(EntityCondensed):
    """
    Represents a Qlik Sense App with limited attribution
    """
    app_id: str = field(default=None, hash=False)
    published_date: datetime = field(default=None, hash=False)
    is_published: bool = field(default=False, hash=False)
    stream: StreamCondensed = field(default=None, hash=False)
    saved_in_product_version: str = field(default=None, hash=False)
    migration_hash: str = field(default=None, hash=False)
    availability_status: str = field(default=None, hash=False)


class AppCondensedSchema(EntityCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense App object with limited attribution
    """
    app_id = ma.fields.Str(required=False, data_key='appId')
    published_date = ma.fields.DateTime(required=False, data_key='publishTime')
    is_published = ma.fields.Bool(required=False, data_key='published')
    stream = ma.fields.Nested(StreamCondensedSchema, many=False, required=False)
    saved_in_product_version = ma.fields.Str(required=False, data_key='savedInProductVersion')
    migration_hash = ma.fields.Str(required=False, data_key='migrationHash')
    availability_status = ma.fields.Str(required=False, data_key='availabilityStatus')

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'AppCondensed':
        return AppCondensed(**data)


@dataclass(unsafe_hash=True)
class App(AppCondensed, Entity):
    """
    Represents a Qlik Sense App with full attribution
    """
    custom_properties: List[CustomPropertyValue] = field(default_factory=list, hash=False)
    owner: UserCondensed = field(default=None, hash=True)
    source_app_id: str = field(default=None, hash=False)
    target_app_id: str = field(default=None, hash=False)
    tags: List[TagCondensed] = field(default_factory=list, hash=False)
    description: str = field(default=None, hash=False)
    file_size: int = field(default=None, hash=False)
    last_reload_time: datetime = field(default=None, hash=False)
    thumbnail: str = field(default=None, hash=False)
    dynamic_color: str = field(default=None, hash=False)


class AppSchema(AppCondensedSchema, EntitySchema):
    """
    A marshmallow schema corresponding to a Qlik Sense App object with full attribution
    """
    custom_properties = ma.fields.Nested(nested=CustomPropertyValueSchema, many=True, required=False,
                                         data_key='customProperties')
    owner = ma.fields.Nested(UserCondensedSchema, many=False, required=True)
    source_app_id = ma.fields.UUID(required=False, data_key='sourceAppId')
    target_app_id = ma.fields.UUID(required=False, data_key='targetAppId')
    tags = ma.fields.Nested(TagCondensedSchema, many=True, required=False)
    description = ma.fields.Str(required=False)
    file_size = ma.fields.Int(required=False, data_key='fileSize')
    last_reload_date = ma.fields.DateTime(required=False, data_key='lastReloadTime')
    thumbnail = ma.fields.Str(required=False)
    dynamic_color = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'App':
        return App(**data)


@dataclass(unsafe_hash=True)
class AppExport:
    """
    Represents a Qlik Sense App Export
    """
    schema_path: str = field(default=None, hash=False)
    export_token: str = field(default=None, hash=True)
    app_id: str = field(default=None, hash=True)
    download_path: str = field(default=None, hash=False)
    is_cancelled: bool = field(default=False, hash=True)


class AppExportSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense App Export object
    """
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')
    export_token = ma.fields.UUID(required=True, data_key='exportToken')
    app_id = ma.fields.UUID(required=True, data_key='appId')
    download_path = ma.fields.Str(required=False, data_key='downloadPath')
    is_cancelled = ma.fields.Bool(required=True, data_key='cancelled')

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'AppExport':
        return AppExport(**data)
