from pydantic.dataclasses import dataclass
import dataclasses
from pydjinni.regex_datatypes import CppTypename, JavaClass, JavaPrimitive, JniTypeSignature
from pathlib import Path


@dataclass
class Metadata:
    position: int
    position_end: int

@dataclass(kw_only=True)
class Type:
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
    _metadata: Metadata = None

    cpp: CppType = None
    objc: ObjcType = None
    objcpp: ObjCppType = None
    java: JavaType = None
    jni: JniType = None


@dataclass
class Enum(Type):
    @dataclass
    class Item:
        name: str
        comment: str | None

    items: list[Item]


@dataclass
class Flags(Type):
    @dataclass
    class Flag:
        name: str
        comment: str | None
        all: bool
        none: bool

    flags: list[Flag]


@dataclass
class TypeReference:
    metadata: Metadata
    name: str
    type: Type | None = None


@dataclass
class Interface(Type):

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
class Record(Type):

    @dataclass
    class Field:
        name: str
        comment: str | None
        type_reference: TypeReference

    fields: list[Field]
