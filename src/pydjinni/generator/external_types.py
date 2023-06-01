from typing import Generic, TypeVar

from pydantic import BaseModel

from pydjinni.parser.base_models import BaseExternalType

ExternalTypeDef = TypeVar("ExternalTypeDef")


class ExternalTypes(BaseModel, Generic[ExternalTypeDef]):
    i8: ExternalTypeDef = BaseExternalType(
        name='i8',
        primitive=BaseExternalType.Primitive.int,
        comment="8 bit integer type"
    )
    i16: ExternalTypeDef = BaseExternalType(
        name='i16',
        primitive=BaseExternalType.Primitive.int,
        comment="16 bit integer type"
    )


class ExternalTypesBuilder:
    def __init__(self, external_base_type: type[BaseModel]):
        self._external_base_type = external_base_type
        self._external_types: dict[str, ExternalTypes] = {}

    def register(self, key: str, external_types: ExternalTypes):
        self._external_types[key] = external_types

    def build(self) -> list:
        output = []
        for field, model in ExternalTypes.model_fields.items():
            field_kwargs = {key: getattr(external_types, field) for key, external_types in self._external_types.items()}
            output.append(self._external_base_type(
                name=model.default.name,
                primitive=model.default.primitive,
                comment=model.default.comment,
                **field_kwargs
            ))
        return output

