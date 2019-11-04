from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import marshmallow as ma


@dataclass(unsafe_hash=True)
class CustomPropertyDefinitionCondensed:
    """
    Represents a Qlik Sense Custom Property Definition with limited attribution
    """
    id: str = field(default=None, hash=True)
    privileges: List[str] = field(default_factory=list, hash=False)
    name: str = field(default=None, hash=True)
    value_type: str = field(default=None, hash=False)
    value_choices: List[str] = field(default_factory=list, hash=False)


@dataclass(unsafe_hash=True)
class CustomPropertyDefinition(CustomPropertyDefinitionCondensed):
    """
    Represents a Qlik Sense Custom Property Definition with full attribution
    """
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_by: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
    object_types: List[str] = field(default_factory=list, hash=False)
    description: str = field(default=None, hash=False)


@dataclass(unsafe_hash=True)
class CustomPropertyValue:
    """
    Represents a Qlik Sense Custom Property Value
    """
    id: str = field(default=None, hash=True)
    created_date: datetime = field(default=None, hash=False)
    modified_date: datetime = field(default=None, hash=False)
    modified_by: str = field(default=None, hash=False)
    schema_path: str = field(default=None, hash=False)
    value: str = field(default=None, hash=True)
    definition: CustomPropertyDefinitionCondensed = field(default=None, hash=True)


class CustomPropertyDefinitionCondensedSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense Custom Property Definition object with limited attribution
    """
    id = ma.fields.UUID(required=False)
    privileges = ma.fields.List(cls_or_instance=str, required=False)
    name = ma.fields.Str(required=True)
    value_type = ma.fields.Str(required=True, data_key='valueType')
    value_choices = ma.fields.List(cls_or_instance=str, required=False, data_key='choiceValues')

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'CustomPropertyDefinitionCondensed':
        return CustomPropertyDefinitionCondensed(**data)


class CustomPropertyDefinitionSchema(CustomPropertyDefinitionCondensedSchema):
    """
    A marshmallow schema corresponding to a Qlik Sense Custom Property Definition object with full attribution
    """
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_by = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')
    object_types = ma.fields.List(cls_or_instance=str, required=False, data_key='objectTypes')
    description = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'CustomPropertyDefinition':
        return CustomPropertyDefinition(**data)


class CustomPropertyValueSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a Qlik Sense Custom Property Value object
    """
    id = ma.fields.UUID(required=False)
    created_date = ma.fields.DateTime(required=False, data_key='createdDate')
    modified_date = ma.fields.DateTime(required=False, data_key='modifiedDate')
    modified_by = ma.fields.Str(required=False, data_key='modifiedByUserName')
    schema_path = ma.fields.Str(required=False, data_key='schemaPath')
    value = ma.fields.Str(required=True)
    definition = ma.fields.Nested(nested=CustomPropertyDefinitionCondensedSchema, many=False, required=True)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'CustomPropertyDefinition':
        return CustomPropertyDefinition(**data)
