from pydantic import BaseModel
from pydjinni.generator.cpp import cpp_target
from pydjinni.generator.java import java_target
from pydjinni.generator.objc import objc_target
from pydjinni.parser.type_factory import TypeFactory


class Metadata(BaseModel):
    """
    Location metadata of a type. Gives the character location in the parsed input file
    """
    position: int
    position_end: int


Type = TypeFactory() \
        .add_target(cpp_target) \
        .add_target(java_target) \
        .add_target(objc_target) \
        .build()

class InternalType(Type):
    """
    Type that has been parsed from an IDL file.
    The location information in the file is stored in the Metadata field
    """
    metadata: Metadata


class Enum(InternalType):

    class Item(BaseModel):
        name: str
        comment: str | None

    items: list[Item]




class Flags(InternalType):

    class Flag(BaseModel):
        name: str
        comment: str | None
        all: bool
        none: bool

    flags: list[Flag]


class TypeReference(BaseModel):
    metadata: Metadata
    name: str
    type: Type | None = None



class Interface(InternalType):

    class Method(BaseModel):

        class Parameter(BaseModel):
            name: str
            type_reference: TypeReference

        name: str
        comment: str | None
        parameters: list[Parameter]
        return_type_reference: TypeReference | None
        static: bool

    methods: list[Method]



class Record(InternalType):

    class Field(BaseModel):
        name: str
        comment: str | None
        type_reference: TypeReference

    fields: list[Field]
