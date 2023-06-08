from pydjinni.parser.base_models import BaseType, BaseField, BaseClassType, TypeReference


class Enum(BaseType):
    class Item(BaseField):
        ...

    items: list[Item]


class Flags(BaseType):
    class Flag(BaseField):
        all: bool
        none: bool

    flags: list[Flag]


class Interface(BaseClassType):
    class Method(BaseField):
        class Parameter(BaseField):
            type_ref: TypeReference

        parameters: list[Parameter]
        return_type_ref: TypeReference | None
        static: bool
        const: bool

    methods: list[Method]


class Record(BaseClassType):
    class Field(BaseField):
        type_ref: TypeReference

    fields: list[Field]
    deriving_eq: bool
    deriving_ord: bool
    deriving_json: bool
