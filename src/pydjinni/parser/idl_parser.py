# Copyright 2023 - 2026 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Final, cast, get_origin, override

from antlr4 import CommonTokenStream, InputStream, ParserRuleContext
from more_itertools import always_iterable

from pydjinni.parser.grammar.IdlLexer import IdlLexer
from pydjinni.parser.grammar.IdlParser import IdlParser
from pydjinni.parser.grammar.IdlVisitor import IdlVisitor
from pydjinni.parser.idl_error_listener import IdlErrorListener
from pydjinni.parser.model.elements import (
    ClassType,
    Comment,
    CommentLine,
    Element,
    Enum,
    ErrorDomain,
    ExternTypeReference,
    FileReference,
    Flags,
    Function,
    ImportReference,
    Interface,
    NamedElement,
    Namespace,
    Parameter,
    Record,
    ResolvedFileReference,
    Type,
    TypeReference,
)
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.model.namespace_tuple import NamespaceTuple
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.providers.namespace_stack import NamespaceStackProvider
from pydjinni.position import Cursor, Position
lazy from pydjinni.file.file_reader_writer import FileReaderWriter
lazy from pydjinni.parser.factories.named_element_factory import NamedElementFactory
lazy from pydjinni.parser.processing.parsetree_processor import ParsetreeProcessor


@dataclass
class IdlParserImpl(IdlVisitor):
    """PyDjinni IDL parser.

    This implements the generated ANTRL4 Visitor interface and applies the given ``ParseTreeProcessor``
    to validate and process the generated abstract syntax tree.
    """

    def __init__(
        self,
        processor: ParsetreeProcessor,
        default_deriving: frozenset[Record.Deriving],
        file_reader: FileReaderWriter,
        named_element_factory: NamedElementFactory,
        file_reference: ResolvedFileReference,
    ):
        self._processor: Final = processor
        self._default_deriving: Final = default_deriving
        self._file_reader: Final = file_reader
        self._file_reference: Final = file_reference
        self._named_element_factory: Final = named_element_factory

        self._error_listener: Final = IdlErrorListener(self._file_reference.resolved_path)
        self._namespace_stack: Final = NamespaceStackProvider()

        self._parser: Final = self._setup_parser(
            self._setup_lexer(self._file_reference.resolved_path),
        )

    def _setup_lexer(self, filename: Path) -> IdlLexer:
        lexer: Final = IdlLexer(input=InputStream(self._file_reader.read_idl(filename)))
        lexer.removeErrorListeners()
        lexer.addErrorListener(self._error_listener)
        return lexer

    def _setup_parser(self, lexer: IdlLexer) -> IdlParser:
        parser: Final = IdlParser(input=CommonTokenStream(lexer))
        parser.removeErrorListeners()
        parser.addErrorListener(self._error_listener)
        return parser

    def _visit[T](self, ctx: ParserRuleContext | None, element_type: type[T]) -> T:
        assert ctx is not None, "context must not be none in non-optional visit"
        result = self.visit(ctx)
        if result is None or not isinstance(result, get_origin(element_type) or element_type):
            raise ValueError(
                f"{type(ctx).__name__} visitor returned {type(result).__name__}; expected {element_type!r}"
            )
        return result

    def _visit_optional[T](self, ctx: ParserRuleContext | None, element_type: type[T]) -> T | None:
        if ctx is not None:
            return self._visit(ctx, element_type)

    def _visit_iterable[T](self, ctx: ParserRuleContext | None, element_type: type[T]) -> Iterable[T]:
        assert isinstance(ctx, Iterable), "context must be iterable"
        for item in cast("Iterable[object]", ctx):
            assert isinstance(item, ParserRuleContext), "context iterable result must be ParserRuleContext"
            yield self._visit(item, element_type)

    def _position(
        self,
        context: ParserRuleContext,
    ) -> Position:

        assert context is not None, "Context must not be none to calculate position"
        assert context.start
        assert context.stop

        return Position(
            file=self._file_reference.resolved_path,
            start=Cursor(
                line=context.start.line - 1,
                col=context.start.column,
            ),
            end=Cursor(
                line=context.stop.line - 1,
                col=context.stop.column + len(context.stop.text),
            ),
        )

    @override
    def visitIdl(self, ctx: IdlParser.IdlContext) -> Iterable[Element]:  # pyright: ignore[reportIncompatibleMethodOverride]
        load: Final = self._visit_iterable(ctx.load(), Element)
        namespace_content: Final = self._visit_iterable(ctx.namespaceContent(), NamedElement)

        return chain(load, namespace_content)

    @override
    def visitComment(self, ctx: IdlParser.CommentContext) -> Comment:  # pyright: ignore[reportIncompatibleMethodOverride]
        return Comment(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            lines=tuple(self._visit_iterable(ctx.commentLine(), CommentLine)),
        )

    @override
    def visitCommentLine(self, ctx: IdlParser.CommentLineContext) -> CommentLine:  # pyright: ignore[reportIncompatibleMethodOverride]
        col_offset = 1
        return CommentLine(
            position=self._position(context=ctx).with_offset(start=Cursor(col=col_offset)),
            namespace=self._namespace_stack.current,
            content=str(ctx.COMMENT())[col_offset:],
        )

    @override
    def visitImportDef(self, ctx: IdlParser.ImportDefContext) -> ImportReference:  # pyright: ignore[reportIncompatibleMethodOverride]
        return ImportReference(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            file_reference=self._visit(ctx.filepath(), FileReference),
        )

    @override
    def visitExtern(self, ctx: IdlParser.ExternContext) -> ExternTypeReference:  # pyright: ignore[reportIncompatibleMethodOverride]
        return ExternTypeReference(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            file_reference=self._visit(ctx.filepath(), FileReference),
        )

    @override
    def visitFilepath(self, ctx: IdlParser.FilepathContext) -> FileReference:  # pyright: ignore[reportIncompatibleMethodOverride]
        return FileReference(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            path=Path(str(ctx.FILEPATH())[1:-1]),
            parent=self._file_reference,
        )

    @override
    def visitNamespace(self, ctx: IdlParser.NamespaceContext) -> Namespace:  # pyright: ignore[reportIncompatibleMethodOverride]
        namespace = self._visit(ctx.namespaceIdentifier(), NamespaceTuple)
        self._namespace_stack.push(namespace)
        try:
            named_elements: Final = tuple(self._visit_iterable(ctx.namespaceContent(), NamedElement))

            return self._named_element_factory.create_namespace(
                position=self._position(ctx),
                namespace=self._namespace_stack.current.parent() or NamespaceTuple(()),
                name=namespace.values[-1],
                comment=self._visit_optional(ctx.comment(), Comment),
                types=tuple(item for item in named_elements if isinstance(item, Type)),
                namespaces=tuple(item for item in named_elements if isinstance(item, Namespace)),
            )
        finally:
            self._namespace_stack.pop()

    @override
    def visitNamespaceIdentifier(self, ctx: IdlParser.NamespaceIdentifierContext) -> NamespaceTuple:  # pyright: ignore[reportIncompatibleMethodOverride]
        return NamespaceTuple(
            values=tuple(self._visit_iterable(ctx.identifier(), Identifier)),
        )

    @override
    def visitEnum(self, ctx: IdlParser.EnumContext) -> Enum:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_enum(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            items=tuple(self._visit_iterable(ctx.item(), Enum.Item)),
        )

    @override
    def visitItem(self, ctx: IdlParser.ItemContext) -> Enum.Item:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_enum_item(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
        )

    @override
    def visitFlags(self, ctx: IdlParser.FlagsContext) -> Flags:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_flags(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            flags=tuple(self._visit_iterable(ctx.flag(), Flags.Flag)),
        )

    @override
    def visitFlag(self, ctx: IdlParser.FlagContext) -> Flags.Flag:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_flags_flag(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            modifier=self._visit_optional(ctx.modifier(), Flags.Flag.Modifier),
        )

    @override
    def visitModifier(self, ctx: IdlParser.ModifierContext) -> Flags.Flag.Modifier | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        return Flags.Flag.Modifier.ALL if ctx.ALL() else Flags.Flag.Modifier.NONE

    @override
    def visitTarget(self, ctx: IdlParser.TargetContext) -> ClassType.Target:  # pyright: ignore[reportIncompatibleMethodOverride]
        return ClassType.Target(str(ctx.HOST() or ctx.NATIVE() or ctx.SHARED()))

    @override
    def visitRecord(self, ctx: IdlParser.RecordContext) -> Record:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_record(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            target=self._visit_optional(ctx.target(), ClassType.Target) or ClassType.Target.shared,
            fields=tuple(self._visit_iterable(ctx.field(), Record.Field)),
            deriving=(self._visit_optional(ctx.deriving(), frozenset[Record.Deriving]) or frozenset())
            | self._default_deriving,
        )

    @override
    def visitField(self, ctx: IdlParser.FieldContext) -> Record.Field:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_record_field(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            reference=self._visit(ctx.typeReference(), TypeReference),
        )

    @override
    def visitTypeReference(self, ctx: IdlParser.TypeReferenceContext) -> TypeReference:  # pyright: ignore[reportIncompatibleMethodOverride]
        if function_context := ctx.function():
            function: Final = self._visit(function_context, Function)
            return TypeReference(
                position=self._position(ctx),
                namespace=self._namespace_stack.current,
                name=function.name,
                namespace_prefix=NamespaceTuple(),
                parameters=(),
                inline_function=function,
            )
        else:
            return self._visit(ctx.dataType(), TypeReference)

    @override
    def visitDataType(self, ctx: IdlParser.DataTypeContext) -> TypeReference:  # pyright: ignore[reportIncompatibleMethodOverride]
        *namespace_values, name = self._visit_iterable(ctx.identifier(), Identifier)
        is_absolute = ctx.start is not None and ctx.start.type == IdlParser.DOT
        return TypeReference(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=name,
            namespace_prefix=NamespaceTuple(tuple(namespace_values)),
            absolute=is_absolute,
            optional=ctx.OPTIONAL() is not None,
            parameters=tuple(self._visit_iterable(ctx.dataType(), TypeReference)),
        )

    @override
    def visitFunction(self, ctx: IdlParser.FunctionContext) -> Function:  # pyright: ignore[reportIncompatibleMethodOverride]
        return_type_reference: Final = self._visit_optional(ctx.typeReference(), TypeReference)
        parameters: Final = tuple(self._visit_iterable(ctx.parameter(), Parameter))
        target: Final = self._visit_optional(ctx.target(), ClassType.Target) or ClassType.Target.shared
        throwing: Final = tuple(always_iterable(self._visit_optional(ctx.throwing(), Iterable[TypeReference])))

        def signature(type_ref: TypeReference, depth: int = 2) -> str:
            generic_signatures: Final = tuple(signature(param, depth + 1) for param in type_ref.parameters)
            return ("_" * depth).join((type_ref.name.value,) + generic_signatures)

        name = "_".join(
            chain(
                ("function", target),
                (signature(parameter.reference) for parameter in parameters),
                (signature(return_type_reference) if return_type_reference else "void",),
                ("throws",) if throwing else (),
                (ref.name.value for ref in throwing),
            )
        )
        return self._named_element_factory.create_function(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=Identifier(name),
            comment=None,
            target=target,
            return_reference=return_type_reference,
            anonymous=True,
            parameters=parameters,
            throwing=throwing,
        )

    @override
    def visitThrowing(self, ctx: IdlParser.ThrowingContext) -> Iterable[TypeReference]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._visit_iterable(ctx.typeReference(), TypeReference)

    @override
    def visitParameter(self, ctx: IdlParser.ParameterContext) -> Parameter:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_parameter(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            reference=self._visit(ctx.typeReference(), TypeReference),
        )

    @override
    def visitDeriving(self, ctx: IdlParser.DerivingContext) -> frozenset[Record.Deriving]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return frozenset(self._visit_iterable(ctx.declaration(), Record.Deriving))

    @override
    def visitDeclaration(self, ctx: IdlParser.DeclarationContext) -> Record.Deriving:  # pyright: ignore[reportIncompatibleMethodOverride]
        return Record.Deriving(str(ctx.EQ() or ctx.ORD()))

    @override
    def visitInterface(self, ctx: IdlParser.InterfaceContext) -> Interface:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_interface(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            target=self._visit_optional(ctx.target(), ClassType.Target) or ClassType.Target.shared,
            params=(),
            methods=tuple(self._visit_iterable(ctx.method(), Interface.Method)),
            properties=tuple(self._visit_iterable(ctx.property_(), Interface.Property)),
        )

    @override
    def visitNamedFunction(self, ctx: IdlParser.NamedFunctionContext) -> Function:  # pyright: ignore[reportIncompatibleMethodOverride]
        anonymous_function: Final = self._visit(ctx.function(), Function)

        return self._named_element_factory.create_function(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            target=anonymous_function.target,
            return_reference=anonymous_function.return_reference,
            anonymous=False,
            parameters=anonymous_function.parameters,
            throwing=anonymous_function.throwing,
        )

    @override
    def visitMethod(self, ctx: IdlParser.MethodContext) -> Interface.Method:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_interface_method(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            static=ctx.STATIC() is not None,
            const=ctx.CONST() is not None,
            return_reference=self._visit_optional(ctx.typeReference(), TypeReference),
            asynchronous=ctx.ASYNC() is not None,
            parameters=tuple(self._visit_iterable(ctx.parameter(), Parameter)),
            throwing=tuple(always_iterable(self._visit_optional(ctx.throwing(), Iterable[TypeReference]))),
        )

    @override
    def visitErrorDomain(self, ctx: IdlParser.ErrorDomainContext) -> ErrorDomain:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_error_domain(
            name=self._visit(ctx.identifier(), Identifier),
            position=self._position(ctx),
            comment=self._visit_optional(ctx.comment(), Comment),
            error_codes=tuple(self._visit_iterable(ctx.errorCode(), ErrorDomain.ErrorCode)),
            namespace=self._namespace_stack.current,
        )

    @override
    def visitErrorCode(self, ctx: IdlParser.ErrorCodeContext) -> ErrorDomain.ErrorCode:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_error_code(
            name=self._visit(ctx.identifier(), Identifier),
            position=self._position(ctx),
            comment=self._visit_optional(ctx.comment(), Comment),
            parameters=tuple(self._visit_iterable(ctx.parameter(), Parameter)),
            namespace=self._namespace_stack.current,
        )

    @override
    def visitProperty(self, ctx: IdlParser.PropertyContext) -> Interface.Property:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._named_element_factory.create_interface_property(
            position=self._position(ctx),
            namespace=self._namespace_stack.current,
            name=self._visit(ctx.identifier(), Identifier),
            comment=self._visit_optional(ctx.comment(), Comment),
            reference=self._visit(ctx.typeReference(), TypeReference),
            readonly=ctx.READONLY() is not None,
        )

    @override
    def visitIdentifier(self, ctx: IdlParser.IdentifierContext) -> Identifier:  # pyright: ignore[reportIncompatibleMethodOverride]
        return Identifier(value=str(ctx.ID()), position=self._position(ctx))

    def parse(self) -> ParseResult:
        """Start parsing the input.

        Returns:
            ParseResult: all parsed ``Element`` s and validation results from the ``ParseTreeProcessor``
        """
        return self._processor.process(
            ParseResult(
                elements=tuple(self._visit(self._parser.idl(), Iterable[Element])),
                diagnostics=self._error_listener.issues,
            )
        )
