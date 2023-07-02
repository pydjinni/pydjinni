from pydjinni.parser.base_models import BaseType, BaseField, BaseClassType, TypeReference, DocStrEnum


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

        parameters: list[Parameter] = []
        return_type_ref: TypeReference | None = None
        static: bool = False
        const: bool = False

    class Property(BaseField):
        type_ref: TypeReference

    main: bool = False
    methods: list[Method] = []
    properties: list[Property] = []


class Record(BaseClassType):
    class Field(BaseField):
        type_ref: TypeReference

    class Deriving(DocStrEnum):
        init = 'init', """
        Generate a default record constructor
        """
        eq = 'eq', """
        Equality operator. 
        All fields in the record are compared in the order they appear in the record declaration. 
        If you need to add a field later, make sure the order is correct.
        """
        ord = 'ord', """
        Ordering comparison.
        Is not supported for collection types, optionals, and booleans.
        """
        str = 'str', """
        String representation of a record instance.
        """
        parcelable = 'parcelable', """
        Instances can be written to and restored from a Parcel (Android)
        """

    fields: list[Field] = []
    deriving: set[Deriving] = set()
