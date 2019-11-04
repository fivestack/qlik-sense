from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import marshmallow as ma


@dataclass(unsafe_hash=True)
class TagCondensed:
    """
    Represents a Qlik Sense Tag with limited attribution
    """
    id: str = field(default=None, hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    name: str = field(default=None, hash=True)


@dataclass(unsafe_hash=True)
class Tag(TagCondensed):
    """
    Represents a Qlik Sense Tag with full attribution
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_user: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)


class TagCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense Tag object with limited attribution
    """
    id = ma.fields.UUID(required=False)
    privileges = ma.fields.List(cls_or_instance=str, required=False)
    name = ma.fields.Str(required=True)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'TagCondensed':
        return TagCondensed(**data)


class TagSchema(TagCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Tag object with full attribution
    """
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_user = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'Tag':
        return Tag(**data)
