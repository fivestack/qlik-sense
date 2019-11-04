"""
These are the models and schemas for the Qlik Sense App domain
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

import marshmallow as ma

from .stream import StreamCondensed, StreamCondensedSchema
from .user import UserCondensed, UserCondensedSchema
from .tag import TagCondensedSchema, TagCondensed
from .custom_property import CustomPropertyValueSchema, CustomPropertyValue


@dataclass(unsafe_hash=True)
class AppCondensed:
    """
    Represents a Qlik Sense App with limited attribution
    """
    id: str = field(default=None, hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    name: str = field(default=None, hash=True)
    app_id: str = field(default=None, hash=False)
    published_date: datetime = field(default=None, hash=False)
    is_published: bool = field(default=False, hash=False)
    stream: StreamCondensed = field(default=None, hash=False)
    saved_in_product_version: str = field(default=None, hash=False)
    migration_hash: str = field(default=None, hash=False)
    availability_status: str = field(default=None, hash=False)


@dataclass(unsafe_hash=True)
class App(AppCondensed):
    """
    Represents a Qlik Sense App with full attribution
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_user: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
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


class AppCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense App object with limited attribution
    """
    id = ma.fields.UUID(required=False)
    privileges = ma.fields.List(cls_or_instance=str, required=False)
    name = ma.fields.Str(required=True)
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


class AppSchema(AppCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense App object with full attribution
    """
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_user = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')
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
