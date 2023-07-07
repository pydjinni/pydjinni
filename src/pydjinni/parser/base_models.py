from __future__ import annotations

from pydjinni.parser.identifier import Identifier
from pydjinni.parser.namespace import Namespace

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum
from enum import Enum, auto
from pydantic import BaseModel, Field



class DocStrEnum(StrEnum):
    def __new__(cls, value, doc=None):
        member = str.__new__(cls, value)
        member._value_ = value
        member.__doc__ = doc.strip()
        return member


class BaseExternalType(BaseModel, validate_assignment=True):
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


class BaseType(BaseExternalType, extra='allow'):
    position: int = -1
    dependencies: list[TypeReference] = []


class TypeReference(BaseModel):
    name: Identifier
    namespace: Namespace | list[Identifier] = []
    position: int = -1
    parameters: list[TypeReference] = []
    optional: bool = False
    type_def: BaseExternalType = Field(
        default=None,
        repr=False
    )


class BaseField(BaseModel, extra='allow'):
    name: Identifier
    position: int = -1
    comment: list[str] | None = None


class Assignment(BaseModel):
    key: str
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
