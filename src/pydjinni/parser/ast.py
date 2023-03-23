from pydantic.dataclasses import dataclass
import dataclasses
from pydjinni.regex_datatypes import CppTypename, JavaClass, JavaPrimitive, JniTypeSignature
from pathlib import Path


@dataclass
class Metadata:
    """
    Location metadata of a type. Gives the character location in the parsed input file
    """
    position: int
    position_end: int

@dataclass(kw_only=True)
class Type:
    """
    Public type interface that defines all the required information for the code generator
    """
    @dataclass
    class CppType:
        typename: CppTypename
        header: Path

    @dataclass
    class ObjcType:
        typename: str
        boxed: str
        header: Path
        pointer: bool

    @dataclass
    class ObjCppType:
        translator: CppTypename
        header: Path

    @dataclass
    class JavaType:
        """Java type information"""
        typename: JavaPrimitive
        boxed: JavaClass
        reference: bool
        generic: bool

    @dataclass
    class JniType:
        translator: CppTypename
        header: Path
        typename: str
        type_signature: JniTypeSignature

    name: str = dataclasses.field(
        default=None,
        metadata=dict(
            description="The name of the type in the interface definition"
        )
    )
    comment: str = dataclasses.field(
        default=None,
        metadata=dict(
            description="A comment describing the type"
        )
    )

    cpp: CppType = None
    objc: ObjcType = None
    objcpp: ObjCppType = None
    java: JavaType = None
    jni: JniType = None

@dataclass
class InternalType(Type):
    """
    Type that has been parsed from an IDL file.
    The location information in the file is stored in the Metadata field
    """
    metadata: Metadata

@dataclass
class Enum(InternalType):
    @dataclass
    class Item:
        name: str
        comment: str | None

    items: list[Item]



@dataclass
class Flags(InternalType):
    @dataclass
    class Flag:
        name: str
        comment: str | None
        all: bool
        none: bool

    flags: list[Flag]

@dataclass(kw_only=True)
class TypeReference:
    metadata: Metadata
    name: str
    type: Type | None = None


@dataclass
class Interface(InternalType):

    @dataclass
    class Method:
        @dataclass
        class Parameter:
            name: str
            type_reference: TypeReference

        name: str
        comment: str | None
        parameters: list[Parameter]
        return_type_reference: TypeReference | None
        static: bool

    methods: list[Method]


@dataclass
class Record(InternalType):

    @dataclass
    class Field:
        name: str
        comment: str | None
        type_reference: TypeReference

    fields: list[Field]
