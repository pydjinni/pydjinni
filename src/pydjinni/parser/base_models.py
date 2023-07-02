from __future__ import annotations
try:
    from enum import StrEnum
except ImportError:
    from strenum import LowercaseStrEnum as StrEnum
from enum import Enum, auto
from pydantic import BaseModel, Field

from pydjinni.parser.identifier import Identifier


class DocStrEnum(StrEnum):
    def __new__(cls, value, doc=None):
        member = str.__new__(cls, value)
        member._value_ = value
        member.__doc__ = doc.strip()
        return member


class BaseExternalType(BaseModel):
    class Primitive(StrEnum):
        none = auto()
        int = auto()
        float = auto()
        double = auto()
        string = auto()
        bool = auto()
        interface = auto()
        record = auto()
        enum = auto()
        flags = auto()

    name: str = Field(
        description="Name of the type in the IDL"
    )
    namespace: str = Field(
        default=None,
        pattern=r"[_\.\w]+",
        description="Optional namespace that the type lives in"
    )
    primitive: Primitive = Field(
        default=Primitive.none,
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
    optional: bool = False
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
