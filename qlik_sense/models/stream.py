from dataclasses import dataclass, field
from typing import List

import marshmallow as ma

from .base import EntityCondensedSchema, EntityCondensed, EntitySchema, Entity
from .user import UserCondensed, UserCondensedSchema
from .tag import TagCondensedSchema, TagCondensed
from .custom_property import CustomPropertyValueSchema, CustomPropertyValue


@dataclass(unsafe_hash=True)
class StreamCondensed(EntityCondensed):
    """
    Represents a Qlik Sense Stream with limited attribution
    """
    id: str = field(default=None, hash=True)


class StreamCondensedSchema(EntityCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Stream object with limited attribution
    """
    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'StreamCondensed':
        return StreamCondensed(**data)


@dataclass(unsafe_hash=True)
class Stream(StreamCondensed, Entity):
    """
    Represents a Qlik Sense Stream with full attribution
    """
    custom_properties: List[CustomPropertyValue] = field(default_factory=list, hash=False)
    owner: UserCondensed = field(default_factory=UserCondensed, hash=False)
    tags: List[TagCondensed] = field(default_factory=list, hash=False)


class StreamSchema(StreamCondensedSchema, EntitySchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Stream object with full attribution
    """
    custom_properties = ma.fields.Nested(nested=CustomPropertyValueSchema, many=True, required=False,
                                         data_key='customProperties')
    owner = ma.fields.Nested(UserCondensedSchema, many=False, required=True)
    tags = ma.fields.Nested(TagCondensedSchema, many=True, required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'Stream':
        return Stream(**data)
