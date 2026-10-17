import re
from abc import ABC
from enum import IntEnum, StrEnum, auto
from functools import cached_property
from itertools import chain
from pathlib import Path
from re import Pattern
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Literal, Self, override

from more_itertools import always_iterable
from pydantic import BaseModel, ConfigDict, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema
lazy from marko.block import Document
lazy from pydantic.json_schema import JsonSchemaValue

from pydjinni.parser.comment.abstract_plugins import Command, ParameterCommand
from pydjinni.parser.comment.comment_parser import CommentParser
from pydjinni.parser.comment.copy_with_document import copy_with_document
from pydjinni.parser.comment.plugins import (
    DeprecatedCommand,
    InlineReference,
    ParamCommand,
    ReturnsCommand,
    ThrowsCommand,
)
from pydjinni.parser.model.annotations import Internal
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.model.namespace_tuple import NamespaceTuple
from pydjinni.position import Cursor, Position

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence


class Element(BaseModel, ABC):
    model_config = ConfigDict(frozen=True)
    position: Internal[Position | None] = None
    namespace: NamespaceTuple = NamespaceTuple()

    @property
    def children(self) -> Iterable[Element]:
        return ()


class FileReference(Element):
    path: Path
    parent: ResolvedFileReference | None = None


class ResolvedFileReference(FileReference):
    resolved_path: Path

    @cached_property
    def circular_import_chain(self) -> Sequence[ResolvedFileReference]:
        reference: ResolvedFileReference | None = self
        import_chain: list[ResolvedFileReference] = [self]
        while reference := reference.parent:
            import_chain.append(reference)
            if reference.position and reference.position.file == self.resolved_path:
                return tuple(reversed(import_chain))
        return ()

    @classmethod
    def from_absolute_path(cls, path: Path) -> Self:
        assert path.is_absolute(), "can only be called with an absolute path!"
        return cls(path=path, resolved_path=path)


class ExternTypeReference(Element):
    file_reference: FileReference

    @property
    def children(self) -> Iterable[Element]:
        return (self.file_reference,)


class ImportReference(Element):
    file_reference: FileReference


class TypeReference(Element):
    name: Identifier
    namespace_prefix: NamespaceTuple = NamespaceTuple()
    absolute: bool = False
    optional: bool = False
    parameters: tuple[TypeReference, ...]
    required_resolution: bool = True
    inline_function: Function | None = None

    @property
    @override
    def children(self) -> Iterable[Element]:
        yield from self.parameters
        if self.inline_function:
            yield self.inline_function

    @cached_property
    def key(self) -> str:
        return "." * self.absolute + ".".join(
            i.value
            for i in (
                *self.namespace_prefix.values,
                self.name,
            )
        )


class CommentLine(Element):
    content: str

    @property
    def children(self) -> Iterable[TypeReference]:
        return chain(
            self._match_throw_block(),
            self._match_inline_references(),
        )

    def _match_type_reference(
        self, pattern: Pattern[str], group: str | int = 1, multi_match: bool = False
    ) -> Iterable[TypeReference]:
        segment_pattern = re.compile(r"\w+")

        if self.position:
            stripped_content = self.content.lstrip()
            leading_whitespace = len(self.content) - len(stripped_content)
            content_start = self.position.with_offset(start=Cursor(col=leading_whitespace))
            if multi_match:
                full_type_reference_matches = pattern.finditer(stripped_content)
            else:
                full_type_reference_matches = always_iterable(pattern.match(stripped_content))

            for full_type_reference_match in full_type_reference_matches:
                match_start = Cursor(
                    col=full_type_reference_match.start(group) + leading_whitespace,
                ).relative_to(self.position.start)
                
                if (full_type_reference := full_type_reference_match.group(group)) is not None:
                    *namespace_values, name = (
                        Identifier(
                            segment_match.group(),
                            position=Position.from_match(self.position.file, segment_match).relative_to(match_start),
                        )
                        for segment_match in segment_pattern.finditer(full_type_reference)
                    )
                    yield TypeReference(
                        position=Position.from_match(
                            file=self.position.file,
                            match=full_type_reference_match,
                            group=group,
                        ).relative_to(content_start.start),
                        namespace=self.namespace,
                        name=name,
                        namespace_prefix=NamespaceTuple(tuple(namespace_values)),
                        absolute=full_type_reference.startswith("."),
                        optional=False,
                        parameters=(),
                        required_resolution=False,
                    )

    def _match_throw_block(self) -> Iterable[TypeReference]:
        yield from self._match_type_reference(pattern=ThrowsCommand.pattern(), group="parameter")

    def _match_inline_references(self) -> Iterable[TypeReference]:
        pattern = InlineReference.pattern
        assert isinstance(pattern, Pattern)
        yield from self._match_type_reference(pattern=pattern, multi_match=True)


class Comment(Element):
    lines: tuple[CommentLine, ...]

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        model_schema = handler(source)
        string_schema = core_schema.no_info_after_validator_function(cls.internal, core_schema.str_schema())
        return core_schema.json_or_python_schema(
            json_schema=string_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    string_schema,
                    model_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda comment: comment.raw,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

    @classmethod
    def internal(cls, text: str) -> Self:
        return cls(
            lines=tuple(CommentLine(content=line) for line in text.split("\n")),
        )

    @cached_property
    def raw(self) -> str:
        return dedent("\n".join(line.content for line in self.lines))

    @cached_property
    def parsed(self) -> Document:
        return CommentParser().parse(self.raw)

    @cached_property
    def deprecated(self) -> Document | bool:
        "Searches the parsed comment for the first deprecation block and returns it's value, or `False` otherwise."
        for element in self.parsed.children:
            if isinstance(element, DeprecatedCommand):
                return copy_with_document(self.parsed, element.children) if element.children else True
        return False

    @cached_property
    def returns(self) -> Document | None:
        for element in self.parsed.children:
            if isinstance(element, ReturnsCommand) and element.children:
                return copy_with_document(self.parsed, element.children)

    @cached_property
    def parameters(self) -> Mapping[str, Document]:
        return frozendict(
            {
                element.parameter: copy_with_document(self.parsed, element.children)
                for element in self.parsed.children
                if isinstance(element, ParamCommand)
            }
        )

    @cached_property
    def throws(self) -> Mapping[str, Document]:
        return frozendict(
            {
                element.parameter: copy_with_document(self.parsed, element.children)
                for element in self.parsed.children
                if isinstance(element, ThrowsCommand)
            }
        )

    @cached_property
    def without_commands(self) -> Document:
        elements = [element for element in self.parsed.children if not isinstance(element, Command | ParameterCommand)]
        return copy_with_document(self.parsed, elements)

    @property
    @override
    def children(self) -> Iterable[CommentLine]:
        return self.lines


class NamedElement(Element, ABC):
    name: Identifier
    "Name of the type in the IDL"
    comment: Comment | None = None
    "Description of the type"


class Type(NamedElement, ABC):
    "Abstract base class for all types"

    class Discriminator(StrEnum):
        "Discriminator type used in the `kind` discriminator field"

        primitive = auto()
        collection = auto()
        interface = auto()
        record = auto()
        enum = auto()
        flags = auto()
        function = auto()
        error = auto()

    @cached_property
    def key(self) -> str:
        return "." + ".".join(
            identifier.value
            for identifier in (
                *self.namespace.values,
                self.name,
            )
        )


class Attribute(NamedElement, ABC):
    pass


class TypedAttribute(Attribute, ABC):
    reference: TypeReference

    @property
    @override
    def children(self) -> Iterable[Element]:
        yield self.reference


class SymbolicConstant(Type, ABC):
    class Value(Attribute):
        pass


class ClassType(Type, ABC):
    class Target(StrEnum):
        native = auto()
        host = auto()
        shared = auto()

    target: Target = Target.shared

    @property
    def native(self) -> bool:
        return self.target in (ClassType.Target.native, ClassType.Target.shared)

    @property
    def host(self) -> bool:
        return self.target in (ClassType.Target.host, ClassType.Target.shared)


class GenericType(Type, ABC):
    params: tuple[str, ...] = ()


class Parameter(TypedAttribute):
    pass


class Namespace(NamedElement):
    types: tuple[Type, ...]
    namespaces: tuple[Namespace, ...]

    @property
    @override
    def children(self) -> Iterable[Namespace | Type]:
        return chain(self.types, self.namespaces)


class ErrorDomain(Type):
    kind: Literal[Type.Discriminator.error] = Type.Discriminator.error

    class ErrorCode(Type):
        parameters: tuple[Parameter, ...]

        @property
        @override
        def children(self) -> Iterable[Parameter]:
            return self.parameters

    error_codes: Internal[tuple[ErrorCode, ...]] = ()

    @property
    @override
    def children(self) -> Iterable[ErrorCode]:
        return self.error_codes


class Primitive(Type):
    kind: Literal[Type.Discriminator.primitive] = Type.Discriminator.primitive

    @classmethod
    def internal(
        cls,
        name: str,
        comment: Comment | None = None,
        namespace: NamespaceTuple | None = None,
    ) -> Self:
        return cls(
            name=Identifier(name),
            comment=comment,
            namespace=namespace or NamespaceTuple(),
        )


class Function(ClassType):
    kind: Literal[Type.Discriminator.function] = Type.Discriminator.function
    return_reference: TypeReference | None = None
    anonymous: Internal[bool] = False
    parameters: Internal[tuple[Parameter, ...]] = ()
    throwing: Internal[tuple[TypeReference, ...]] = ()

    @property
    @override
    def children(self) -> Iterable[Parameter | TypeReference]:
        yield from chain(self.parameters, self.throwing)
        if self.return_reference:
            yield self.return_reference


class Record(ClassType):
    kind: Literal[Type.Discriminator.record] = Type.Discriminator.record

    class Deriving(StrEnum):
        eq = auto()
        """
        Equality operator. 
        All fields in the record are compared in the order they appear in the record declaration. 
        If you need to add a field later, make sure the order is correct.
        """
        ord = auto()
        """
        Ordering comparison.
        Is not supported for collection types, optionals, and booleans.
        """

    class Field(TypedAttribute):
        pass

    fields: Internal[tuple[Field, ...]] = ()
    deriving: Internal[frozenset[Deriving]] = frozenset()

    @property
    @override
    def children(self) -> Iterable[Field]:
        return self.fields


class CollectionType(GenericType):
    kind: Literal[Type.Discriminator.collection] = Type.Discriminator.collection

    @classmethod
    def internal(
        cls,
        name: str,
        params: tuple[str, ...],
        comment: Comment | None = None,
        namespace: NamespaceTuple | None = None,
    ) -> Self:
        return cls(
            name=Identifier(name),
            comment=comment,
            namespace=namespace or NamespaceTuple(),
            params=params,
        )


class Interface(GenericType, ClassType):
    kind: Literal[Type.Discriminator.interface] = Type.Discriminator.interface

    class Method(NamedElement):
        static: bool
        const: bool
        return_reference: TypeReference | None
        asynchronous: bool
        parameters: tuple[Parameter, ...]
        throwing: tuple[TypeReference, ...]

        @property
        @override
        def children(self) -> Iterable[Element]:
            yield from chain(
                self.parameters,
                self.throwing,
                super().children,
            )
            if self.return_reference:
                yield self.return_reference

    class Property(TypedAttribute):
        readonly: bool

    methods: Internal[tuple[Method, ...]] = ()
    properties: Internal[tuple[Property, ...]] = ()

    @property
    @override
    def children(self) -> Iterable[Method | Property]:
        return chain(self.methods, self.properties)


class Enum(SymbolicConstant):
    kind: Literal[Type.Discriminator.enum] = Type.Discriminator.enum

    class Item(SymbolicConstant.Value):
        pass

    items: Internal[tuple[Item, ...]] = ()

    @property
    @override
    def children(self) -> Iterable[Item]:
        return self.items


class Flags(SymbolicConstant):
    kind: Literal[Type.Discriminator.flags] = Type.Discriminator.flags

    class Flag(SymbolicConstant.Value):
        class Modifier(IntEnum):
            ALL = auto()
            NONE = auto()

        modifier: Modifier | None

    flags: Internal[tuple[Flag, ...]] = ()

    @property
    @override
    def children(self) -> Iterable[Flag]:
        return self.flags
