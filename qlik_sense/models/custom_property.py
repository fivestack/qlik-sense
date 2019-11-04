from dataclasses import dataclass, field
from typing import List

import marshmallow as ma

from .base import EntityCondensedSchema, EntityCondensed, EntitySchema, Entity, AuditingSchema, Auditing


@dataclass(unsafe_hash=True)
class CustomPropertyDefinitionCondensed(EntityCondensed):
    """
    Represents a Qlik Sense Custom Property Definition with limited attribution
    """
    value_type: str = field(default=None, hash=False)
    value_choices: List[str] = field(default_factory=list, hash=False)


class CustomPropertyDefinitionCondensedSchema(EntityCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Custom Property Definition object with limited attribution
    """
    value_type = ma.fields.Str(required=True, data_key='valueType')
    value_choices = ma.fields.List(cls_or_instance=str, required=False, data_key='choiceValues')

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'CustomPropertyDefinitionCondensed':
        return CustomPropertyDefinitionCondensed(**data)


@dataclass(unsafe_hash=True)
class CustomPropertyDefinition(CustomPropertyDefinitionCondensed, Entity):
    """
    Represents a Qlik Sense Custom Property Definition with full attribution
    """
    object_types: List[str] = field(default_factory=list, hash=False)
    description: str = field(default=None, hash=False)


class CustomPropertyDefinitionSchema(CustomPropertyDefinitionCondensedSchema, EntitySchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Custom Property Definition object with full attribution
    """
    object_types = ma.fields.List(cls_or_instance=str, required=False, data_key='objectTypes')
    description = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'CustomPropertyDefinition':
        return CustomPropertyDefinition(**data)


@dataclass(unsafe_hash=True)
class CustomPropertyValue(Auditing):
    """
    Represents a Qlik Sense Custom Property Value
    """
    id: str = field(default=None, hash=True)
    value: str = field(default=None, hash=True)
    definition: CustomPropertyDefinitionCondensed = field(default=None, hash=True)


class CustomPropertyValueSchema(AuditingSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Custom Property Value object
    """
    id = ma.fields.UUID(required=False)
    value = ma.fields.Str(required=True)
    definition = ma.fields.Nested(nested=CustomPropertyDefinitionCondensedSchema, many=False, required=True)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'CustomPropertyDefinition':
        return CustomPropertyDefinition(**data)
