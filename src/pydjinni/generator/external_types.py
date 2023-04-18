from typing import Generic, TypeVar

from pydantic import BaseModel

ExternalTypeDef = TypeVar("ExternalTypeDef")


class ExternalTypes(BaseModel, Generic[ExternalTypeDef]):
    i8: ExternalTypeDef
    i16: ExternalTypeDef


class ExternalTypesFactory:
    def __init__(self, external_base_type: type[BaseModel]):
        self._external_base_type = external_base_type
        self._external_types: dict[str, ExternalTypes] = {}

    def register(self, key: str, external_types: ExternalTypes):
        self._external_types[key] = external_types

    def build(self) -> list:
        output = []
        for field in ExternalTypes.model_fields:
            field_kwargs = {key: getattr(external_types, field) for key, external_types in self._external_types.items()}
            output.append(self._external_base_type(
                name=field,
                **field_kwargs
            ))
        return output

