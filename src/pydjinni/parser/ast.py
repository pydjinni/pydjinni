from pydantic import BaseModel, Field

from pydjinni.parser.base_models import BaseType, BaseField, BaseExternalType
from pydjinni.parser.identifier import Identifier


class Enum(BaseType):
    class Item(BaseField):
        ...

    items: list[Item]


class Flags(BaseType):
    class Flag(BaseField):
        all: bool
        none: bool

    flags: list[Flag]


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
    value: int | float | str | Identifier


class Constant(BaseModel):
    name: Identifier
    type_ref: TypeReference
    position: int
    value: int | float | str | Identifier | list[Assignment]


class Interface(BaseType):
    class Method(BaseField):
        class Parameter(BaseField):
            type_ref: TypeReference

        parameters: list[Parameter]
        return_type_ref: TypeReference | None
        static: bool

    methods: list[Method]
    constants: list[Constant]
    targets: list[str]


class Record(BaseType):
    class Field(BaseField):
        type_ref: TypeReference

    fields: list[Field]
    constants: list[Constant]
