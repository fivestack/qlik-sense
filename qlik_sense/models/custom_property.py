from dataclasses import dataclass, field, asdict
from typing import List, Union

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
    value_choices = ma.fields.List(cls_or_instance=ma.fields.Str, required=False, allow_none=True,
                                   data_key='choiceValues')

    @ma.pre_dump()
    def pre_dump(self, data: 'Union[CustomPropertyDefinitionCondensed, dict]', **kwargs) -> dict:
        if isinstance(data, CustomPropertyDefinitionCondensed):
            return asdict(data)
        return data

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
    object_types = ma.fields.List(cls_or_instance=ma.fields.Str, required=False, allow_none=True,
                                  data_key='objectTypes')
    description = ma.fields.Str(required=False)

    @ma.pre_dump()
    def pre_dump(self, data: 'Union[CustomPropertyDefinition, dict]', **kwargs) -> dict:
        if isinstance(data, CustomPropertyDefinition):
            return asdict(data)
        return data

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
    definition = ma.fields.Nested(CustomPropertyDefinitionCondensedSchema, many=False, required=True)

    @ma.pre_dump()
    def pre_dump(self, data: 'Union[CustomPropertyValue, dict]', **kwargs) -> dict:
        if isinstance(data, CustomPropertyValue):
            return asdict(data)
        return data

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'CustomPropertyValue':
        return CustomPropertyValue(**data)
