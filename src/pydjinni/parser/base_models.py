from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field

from pydjinni.parser.identifier import Identifier


class BaseExternalType(BaseModel):
    class Primitive(str, Enum):
        int = 'int'
        float = 'float'
        double = 'double'
        string = 'string'
        bool = 'bool'
        interface = 'interface'
        record = 'record'
        enum = 'enum'
        flags = 'flags'

    name: str = Field(
        description="Name of the type in the IDL"
    )
    namespace: str = Field(
        default=None,
        pattern=r"[_\.\w]+",
        description="Optional namespace that the type lives in"
    )
    primitive: Primitive = Field(
        description="The underlying primitive type"
    )
    params: list[str] = []
    comment: str | None = None


class BaseType(BaseModel, extra='allow'):
    name: Identifier
    position: int = -1
    namespace: list[Identifier] = []
    comment: list[str] | None = None
    dependencies: list[TypeReference] = []


class TypeReference(BaseModel):
    name: Identifier
    position: int
    parameters: list[TypeReference]
    type_def: BaseExternalType | BaseType = Field(
        default=None,
        repr=False
    )


class BaseField(BaseModel, extra='allow'):
    name: Identifier
    position: int = -1
    comment: list[str] | None = None


class Assignment(BaseModel):
    key: Identifier
    position: int
    value: int | float | str | bool | Identifier | ObjectValue


class ObjectValue(BaseModel):
    assignments: dict[Identifier, Assignment]


class Constant(BaseField):
    type_ref: TypeReference = None
    value: int | float | str | bool | Identifier | ObjectValue = None


class BaseClassType(BaseType):
    constants: list[Constant] = []
    targets: list[str] = []
