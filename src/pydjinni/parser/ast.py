from typing import Any

from pydantic import BaseModel

from pydjinni.parser.base_models import BaseType, BaseField
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
    type_def: BaseType = None


class Interface(BaseType):
    class Method(BaseField):
        class Parameter(BaseField):
            type_ref: TypeReference

        parameters: list[Parameter]
        return_type_ref: TypeReference | None
        static: bool

    methods: list[Method]


class Record(BaseType):
    class Field(BaseField):
        type_ref: TypeReference

    fields: list[Field]
