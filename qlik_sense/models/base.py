from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import marshmallow as ma


@dataclass(unsafe_hash=True)
class Auditing:
    """
    Represents Qlik Sense auditing fields
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_user: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)


class AuditingSchema(ma.Schema):
    """
    A marshmallow schema corresponding to Qlik Sense auditing fields
    """
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_user = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')


@dataclass(unsafe_hash=True)
class EntityCondensed:
    """
    Represents a Qlik Sense Entity with limited attribution
    """
    id: str = field(default=None, hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    name: str = field(default=None, hash=False)


class EntityCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense Stream object with limited attribution
    """
    id = ma.fields.UUID(required=False)
    privileges = ma.fields.List(cls_or_instance=ma.fields.Str, required=False, allow_none=True)
    name = ma.fields.Str(required=True, allow_none=True)


@dataclass(unsafe_hash=True)
class Entity(EntityCondensed, Auditing):
    """
    Represents a Qlik Sense Entity with full attribution
    """
    id: str = field(default=None, hash=True)


class EntitySchema(EntityCondensedSchema, AuditingSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Stream object with full attribution
    """
