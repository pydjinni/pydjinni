from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    ClassType,
    TypeReference,
    DocStrEnum,
    SymbolicConstantField,
    SymbolicConstantType

)


class Enum(SymbolicConstantType):
    class Item(SymbolicConstantField):
        ...

    items: list[Item]


class Flags(SymbolicConstantType):
    class Flag(SymbolicConstantField):
        all: bool
        none: bool

    flags: list[Flag]


class Parameter(BaseField):
    type_ref: TypeReference


class Interface(ClassType):
    class Method(BaseField):
        parameters: list[Parameter] = []
        return_type_ref: TypeReference | None = None
        static: bool = False
        const: bool = False

    class Property(BaseField):
        type_ref: TypeReference

    main: bool = False
    methods: list[Method] = []
    properties: list[Property] = []


class Function(BaseType):
    parameters: list[Parameter] = []
    return_type_ref: TypeReference | None = None
    targets: list[str] = []


class Record(ClassType):
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
