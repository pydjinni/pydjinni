from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field

from pydjinni.parser.identifier import Identifier


class BaseExternalType(BaseModel):
    class Primitive(str, Enum):
        int = 'int'
        float = 'float'
        string = 'string'
        bool = 'bool'

    name: str = Field(
        description="Name of the type in the IDL"
    )
    namespace: str = Field(
        default=None,
        pattern="[_\.\w]+",
        description="Optional namespace that the type lives in"
    )
    primitive: Primitive | None = Field(
        default=None,
        description="If the type can be assigned primitive values, defines which primitive value the type accepts"
    )
    comment: str | None = None


class BaseType(BaseModel, extra='allow'):
    name: Identifier
    position: int
    namespace: list[Identifier] = []
    comment: list[str] | None = None
    dependencies: list[BaseType | BaseExternalType] = []


class BaseField(BaseModel, extra='allow'):
    name: Identifier
    position: int
    comment: list[str] | None = None


class TypeReference(BaseModel):
    name: Identifier
    position: int
    type_def: BaseExternalType = Field(
        default=None,
        repr=False
    )


class Assignment(BaseModel):
    key: Identifier
    position: int
    value: int | float | str | bool | Identifier | ObjectValue


class ObjectValue(BaseModel):
    assignments: dict[Identifier, Assignment]


class Constant(BaseField):
    type_ref: TypeReference
    value: int | float | str | bool | Identifier | ObjectValue


class BaseClassType(BaseType):
    constants: list[Constant]
