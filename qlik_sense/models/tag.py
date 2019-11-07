from dataclasses import dataclass, field, asdict
from typing import Union

import marshmallow as ma

from .base import EntityCondensedSchema, EntityCondensed, EntitySchema, Entity


@dataclass(unsafe_hash=True)
class TagCondensed(EntityCondensed):
    """
    Represents a Qlik Sense Tag with limited attribution
    """
    id: str = field(default=None, hash=True)


class TagCondensedSchema(EntityCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Tag object with limited attribution
    """
    @ma.pre_dump()
    def pre_dump(self, data: 'Union[TagCondensed, dict]', **kwargs) -> dict:
        if isinstance(data, TagCondensed):
            return asdict(data)
        return data

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'TagCondensed':
        return TagCondensed(**data)


@dataclass(unsafe_hash=True)
class Tag(TagCondensed, Entity):
    """
    Represents a Qlik Sense Tag with full attribution
    """


class TagSchema(TagCondensedSchema, EntitySchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Tag object with full attribution
    """
    @ma.pre_dump()
    def pre_dump(self, data: 'Union[Tag, dict]', **kwargs) -> dict:
        if isinstance(data, Tag):
            return asdict(data)
        return data

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'Tag':
        return Tag(**data)
