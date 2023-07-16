from __future__ import annotations

from functools import cached_property
from pathlib import Path

from pydjinni.parser.identifier import Identifier
from pydjinni.parser.namespace import Namespace

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11
from pydantic import BaseModel, Field, computed_field


class DocStrEnum(StrEnum):
    def __new__(cls, value, doc=None):
        member = str.__new__(cls, value)
        member._value_ = value
        member.__doc__ = doc.strip()
        return member


class Position(BaseModel):
    start: int = None
    end: int = None
    file: Path = None

    @computed_field
    @cached_property
    def length(self) -> int: return self.end - self.start if self.end else None


class BaseExternalType(BaseModel):
    class Primitive(StrEnum):
        none = 'none'
        int = 'int'
        float = 'float'
        double = 'double'
        string = 'string'
        bool = 'bool'
        interface = 'interface'
        record = 'record'
        enum = 'enum'
        flags = 'flags'
        function = 'function'

    name: Identifier = Field(
        description="Name of the type in the IDL"
    )
    namespace: Namespace | list[Identifier] = Field(
        default=[],
        description="Optional namespace that the type lives in"
    )
    primitive: Primitive = Field(
        default=Primitive.none,
        description="The underlying primitive type"
    )
    params: list[str] = []
    comment: str = None

class TypeReference(BaseModel):
    name: Identifier
    namespace: Namespace | list[Identifier] = []
    position: Position = Position()
    parameters: list[TypeReference] = []
    optional: bool = False
    type_def: BaseExternalType = Field(
        default=None,
        repr=False
    )


class BaseType(BaseExternalType, extra='allow'):
    position: Position = Position()
    dependencies: list[TypeReference] = []


class BaseField(BaseModel, extra='allow'):
    name: Identifier
    position: Position = Position()
    comment: list[str] | None = None


class Assignment(BaseModel):
    key: str
    position: Position = Position()
    value: int | float | str | bool | Identifier | ObjectValue


class ObjectValue(BaseModel):
    assignments: dict[Identifier, Assignment]


class Constant(BaseField):
    type_ref: TypeReference = None
    value: int | float | str | bool | Identifier | ObjectValue = None


class ClassType(BaseType):
    constants: list[Constant] = []
    targets: list[str] = []


class SymbolicConstantField(BaseField):
    pass


class SymbolicConstantType(BaseType):
    pass
