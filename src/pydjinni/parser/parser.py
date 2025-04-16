# Copyright 2023 - 2025 jothepro
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

from pathlib import Path

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from antlr4.tree.Tree import ErrorNode
from mistune import BlockState
from pydjinni.exceptions import ApplicationException, FileNotFoundException, ApplicationExceptionList, \
    InputParsingException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.generator.cpp.cpp.generator import CppGenerator
from pydjinni.generator.target import Target
from pydjinni.position import Position, Cursor
from .ast import (
    Record,
    Interface,
    Enum,
    Flags,
    Parameter,
    Function,
    ErrorDomain,
    Namespace
)
from .base_models import BaseType, TypeReference, BaseField, BaseExternalType, DataField, FileReference
from .comment_processor import ParserCommentProcessor
from .grammar.IdlLexer import IdlLexer
from .grammar.IdlParser import IdlParser
from .grammar.IdlVisitor import IdlVisitor
from .identifier import IdentifierType as Identifier
from .markdown_parser import MarkdownParser
from .resolver import Resolver


def unpack(list_input: []):
    return list_input[0] if list_input else None


class Parser(IdlVisitor):
    def __init__(
            self,
            resolver: Resolver,
            targets: list[Target],
            supported_target_keys: list[str],
            include_dirs: list[Path],
            default_deriving: set[Record.Deriving],
            file_reader: FileReaderWriter,
            idl: Path,
            position: Position = None,
    ):
        self.resolver = resolver
        self.targets = targets
        self.target_keys = supported_target_keys
        self.file_reader = file_reader
        self.include_dirs = include_dirs
        self.default_deriving = default_deriving
        self.idl = idl
        self.position = position
        self.type_decls: list[BaseType] = []
        self.field_decls: list[BaseField] = []
        self.type_refs: list[TypeReference] = []
        self.file_imports: list[FileReference] = []
        self.current_namespace: list[Identifier] = []
        self.current_namespace_stack_size: list[int] = []
        self.errors: list[ApplicationException] = []
        self.markdown_parser = MarkdownParser(self.type_refs)

    class ParsingException(ApplicationException, code=150):
        """IDL Parsing error"""

    class ParsingExceptionList(ApplicationExceptionList):
        def __init__(self, errors: list[ApplicationException], type_decls: list[BaseType], type_refs: list[TypeReference], file_imports: list[FileReference], fields: list[BaseField], ast: list[BaseType | Namespace]):
            super().__init__(errors)
            self.type_decls = type_decls
            self.type_refs = type_refs
            self.file_imports = file_imports
            self.fields = fields
            self.ast = ast

    class ParsingErrorListener(ErrorListener):
        def __init__(self, idl: Path, errors: list[Exception]):
            self.idl = idl
            self.errors = errors

        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            self.errors.append(Parser.ParsingException(
                f'{msg}, {offendingSymbol}',
                position=Position(
                    start=Cursor(line=line - 1, col=column),
                    end=Cursor(line=line - 1, col=column),
                    file=self.idl
                )
            ))

    def visitIdl(self, ctx:IdlParser.IdlContext):
        [self.visit(load) for load in ctx.load()]
        return [self.visit(content) for content in ctx.namespaceContent()]

    def visitComment(self, ctx: IdlParser.CommentContext) -> tuple[str, tuple[list, BlockState]]:
        raw_comment = "\n".join([line.getText()[1:] for line in ctx.COMMENT()])
        comment = "\n".join([line.getText()[1:].strip() for line in ctx.COMMENT()])
        return (comment, self.markdown_parser.parse(raw_comment, self.current_namespace, self._position(ctx)))

    def visitTypeDecl(self, ctx: IdlParser.TypeDeclContext):
        type_decl_context = ctx.enum() or ctx.flags() or ctx.record() or ctx.interface() or ctx.namedFunction() or ctx.errorDomain()
        if type_decl_context:
            type_decl: BaseType = self.visit(type_decl_context)
            self.resolver.register(type_decl)
            self.type_decls.append(type_decl)
            return type_decl
        else:
            self.errors.append(Parser.ParsingException(
                "unknown type. Expected enum | flags | record | interface | function | error",
                position=self._position(ctx)
            ))

    def visitIdentifier(self, ctx: IdlParser.IdentifierContext) -> Identifier:
        return Identifier(ctx.ID().getText())

    def visitNsIdentifier(self, ctx: IdlParser.NsIdentifierContext) -> Identifier:
        return Identifier((ctx.ID() or ctx.NS_ID()).getText())

    def visitEnum(self, ctx: IdlParser.EnumContext) -> Enum:
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        result = Enum(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            items=[self.visit(item) for item in ctx.item()],
            namespace=self.current_namespace,
            comment=comment,
        )
        result._parsed_comment = parsed_comment
        return result

    def visitItem(self, ctx: IdlParser.ItemContext) -> Enum.Item:
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        item = Enum.Item(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            comment=comment
        )
        item._parsed_comment = parsed_comment
        self.field_decls.append(item)
        return item

    def visitFlags(self, ctx: IdlParser.FlagsContext) -> Flags:
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        result = Flags(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            flags=[self.visit(flag) for flag in ctx.flag()],
            namespace=self.current_namespace,
            comment=comment,
        )
        result._parsed_comment = parsed_comment
        return result

    def visitFlag(self, ctx: IdlParser.FlagContext):
        all, none = self.visit(ctx.modifier()) if ctx.modifier() else (False, False)
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        flag = Flags.Flag(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            all=all,
            none=none,
            comment=comment
        )
        flag._parsed_comment = parsed_comment
        self.field_decls.append(flag)
        return flag

    def visitModifier(self, ctx: IdlParser.ModifierContext) -> tuple[bool, bool]:
        value = ctx.ID().getText()
        if value not in ["all", "none"]:
            self.errors.append(Parser.ParsingException(
                f"expected 'all' or 'none', got '{value}'",
                position=self._position(ctx)
            ))
        return value == "all", value == "none"

    def visitInterface(self, ctx: IdlParser.InterfaceContext) -> Interface:
        methods: list[Interface.Method] = [self.visit(method) for method in ctx.method()]
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        properties: list[Interface.Property] = [self.visit(prop) for prop in ctx.prop()]
        dependencies: list[TypeReference] = []

        for method in methods:
            for param in method.parameters:
                dependencies.append(param.type_ref)
            if method.throwing:
                for error_domain_ref in method.throwing:
                    dependencies.append(error_domain_ref)
            if method.return_type_ref:
                dependencies.append(method.return_type_ref)
        for prop in properties:
            dependencies.append(prop.type_ref)
        interface = Interface(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            methods=methods,
            targets=self.visit(ctx.targets()) or self.target_keys,
            properties=properties,
            main=ctx.MAIN() is not None,
            namespace=self.current_namespace,
            dependencies=self._dependencies(dependencies),
            comment=comment
        )
        interface._parsed_comment = parsed_comment

        if interface.main and interface.targets != [CppGenerator.key]:
            self.errors.append(
                Parser.ParsingException("a 'main' interface can only be implemented in C++", interface.position))

        for method in interface.methods:
            if not interface.targets == [CppGenerator.key] and method.static:
                self.errors.append(Parser.ParsingException(
                    f"methods are only allowed to be static on '{CppGenerator.key}' interfaces",
                    method.position
                ))

        return interface

    def visitMethod(self, ctx: IdlParser.MethodContext) -> Interface.Method:
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        method = Interface.Method(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            parameters=[self.visit(param) for param in ctx.parameter()],
            return_type_ref=self.visit(ctx.typeRef()) if ctx.typeRef() else None,
            static=ctx.STATIC() is not None,
            const=ctx.CONST() is not None,
            asynchronous=ctx.ASYNC() is not None,
            throwing=self.visit(ctx.throwing()) if ctx.throwing() else None,
            comment=comment
        )
        method._parsed_comment = parsed_comment
        self.field_decls.append(method)
        if method.static and method.const:
            self.errors.append(Parser.ParsingException("method cannot be both static and const", method.position))
        return method

    def visitParameter(self, ctx: IdlParser.ParameterContext) -> Parameter:
        parameter = Parameter(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            type_ref=self.visit(ctx.typeRef())
        )
        self.field_decls.append(parameter)
        return parameter

    def visitThrowing(self, ctx:IdlParser.ThrowingContext) -> list[TypeReference]:
        return [self.visit(typeRef) for typeRef in ctx.typeRef()]


    def visitProp(self, ctx: IdlParser.PropContext) -> Interface.Property:
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        result = Interface.Property(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            comment=comment,
            type_ref=self.visit(ctx.typeRef()) if ctx.typeRef() else None
        )
        result._parsed_comment = parsed_comment
        return result

    def visitTypeRef(self, ctx: IdlParser.TypeRefContext) -> TypeReference:
        if ctx.function():
            function = self.visit(ctx.function())
            self.type_decls.append(function)
            position = self._position(ctx)
            return TypeReference(
                name="<function>",
                position=position,
                identifier_position=position,
                namespace=self.current_namespace,
                type_def=function
            )
        else:
            return self.visit(ctx.dataType())

    def visitDataType(self, ctx: IdlParser.DataTypeContext) -> TypeReference:
        position = self._position(ctx)
        name = self.visit(ctx.nsIdentifier())
        typename = name.rsplit('.', 1)[-1]
        type_ref = TypeReference(
            name=name,
            parameters=[self.visit(param) for param in ctx.dataType()],
            position=position,
            identifier_position=position.with_offset(start=Cursor(col=len(name) - len(typename))),
            namespace=self.current_namespace,
            optional=ctx.OPTIONAL() is not None
        )
        self.type_refs.append(type_ref)
        return type_ref

    def visitFunction(self, ctx: IdlParser.FunctionContext) -> Function:
        targets: list[str] = self.visit(ctx.targets()) or self.target_keys if ctx.FUNCTION() else self.target_keys
        return_type_ref = self.visit(ctx.typeRef()) if ctx.typeRef() else None
        parameters = [self.visit(param) for param in ctx.parameter()]

        dependencies: list[TypeReference] = []
        throwing = self.visit(ctx.throwing()) if ctx.throwing() else None

        for param in parameters:
            dependencies.append(param.type_ref)
        if throwing:
            for error_domain_ref in throwing:
                dependencies.append(error_domain_ref)
        if return_type_ref:
            dependencies.append(return_type_ref)

        def signature(type_ref: TypeReference, depth: int = 2):
            output = type_ref.name
            generic_signatures = []
            for param in type_ref.parameters:
                generic_signatures.append(signature(param, depth + 1))
            return ('_' * depth).join([output] + generic_signatures)

        name = '_'.join(
            ['function'] +
            [target for target in targets] +
            [signature(parameter.type_ref) for parameter in parameters] +
            [signature(return_type_ref) if return_type_ref else 'void'] +
            (["throws"] + [ref.name for ref in throwing] if throwing is not None else [])
        )
        return Function(
            name=Identifier(name),
            position=self._position(ctx),
            identifier_position=self._position(ctx),
            parameters=parameters,
            targets=targets,
            namespace=self.current_namespace,
            return_type_ref=return_type_ref,
            dependencies=dependencies,
            throwing=throwing,
        )

    def visitRecord(self, ctx: IdlParser.RecordContext) -> Record:
        fields = [self.visit(field) for field in ctx.field()]
        deriving = (self.visit(ctx.deriving()) | self.default_deriving) if ctx.deriving() else self.default_deriving
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        record = Record(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            comment=comment,
            fields=fields,
            targets=self.visit(ctx.targets()),
            namespace=self.current_namespace,
            dependencies=self._dependencies([field.type_ref for field in fields]),
            deriving=deriving
        )
        record._parsed_comment = parsed_comment
        return record

    def visitErrorDomain(self, ctx: IdlParser.ErrorDomainContext) -> ErrorDomain:
        error_codes = [self.visit(errorCode) for errorCode in ctx.errorCode()]
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        dependencies = []
        for errorCode in error_codes:
            for param in errorCode.parameters:
                dependencies.append(param.type_ref)
        error_domain = ErrorDomain(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            comment=comment,
            error_codes=error_codes,
            namespace=self.current_namespace,
            dependencies=dependencies,
        )
        error_domain._parsed_comment = parsed_comment
        return error_domain

    def visitErrorCode(self, ctx: IdlParser.ErrorCodeContext) -> ErrorDomain.ErrorCode:
        parameters = [self.visit(parameter) for parameter in ctx.parameter()]
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        error_code = ErrorDomain.ErrorCode(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            comment=comment,
            parameters=parameters,
        )
        error_code._parsed_comment = parsed_comment
        self.field_decls.append(error_code)
        return error_code

    def visitField(self, ctx: IdlParser.FieldContext):
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        field = DataField(
            name=self.visit(ctx.identifier()),
            position=self._position(ctx),
            identifier_position=self._position(ctx.identifier()),
            comment=comment,
            type_ref=self.visit(ctx.typeRef())
        )
        field._parsed_comment = parsed_comment
        if isinstance(field.type_ref.type_def, Function):
            self.errors.append(Parser.ParsingException(
                "functions are not allowed as record field type",
                position=self._position(ctx.typeRef())
            ))
        self.field_decls.append(field)
        return field

    def visitDeriving(self, ctx: IdlParser.DerivingContext) -> set[str]:
        return set(filter(None, [self.visit(decl) for decl in ctx.declaration()]))

    def visitDeclaration(self, ctx: IdlParser.DeclarationContext) -> str:
        value = ctx.ID().getText()
        try:
            return Record.Deriving(value)
        except ValueError:
            self.errors.append(Parser.ParsingException(
                f"'{value}' is not a valid record extension", self._position(ctx))
            )

    def visitNamedFunction(self, ctx: IdlParser.NamedFunctionContext) -> Function:
        function = self.visit(ctx.function())
        function.name = self.visit(ctx.identifier())
        function.position = self._position(ctx)
        function.identifier_position = self._position(ctx.identifier())
        function.anonymous = False
        function.comment, function._parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        return function

    def visitTargets(self, ctx: IdlParser.TargetsContext) -> list[str]:
        includes = []
        excludes = []

        targets: list[str] = [target.getText() for target in ctx.TARGET()]
        if "+any" in targets:
            includes = self.target_keys
        for target in targets:
            if target.startswith('+'):
                includes.append(target[1:])
            else:
                excludes.append(target[1:])
        if (not includes) and excludes:
            includes = self.target_keys

        targets = [include for include in includes if include not in excludes]
        for target in targets:
            if target not in self.target_keys:
                self.errors.append(Parser.ParsingException(
                    f"Unknown interface target '{target}'",
                    self._position(ctx)
                ))
        return targets

    def visitNamespace(self, ctx:IdlParser.NamespaceContext):
        comment, parsed_comment = self.visit(ctx.comment()) if ctx.comment() else (None, None)
        name = Identifier(self.visit(ctx.nsIdentifier()))
        namespace: list[Identifier] = [Identifier(identifier) for identifier in
                                       name.split('.')]
        self.current_namespace += namespace
        self.current_namespace_stack_size.append(len(namespace))

        last_namespace_identifier = name.rsplit('.', 1)[-1]
        result = Namespace(
            comment=comment,
            name=name,
            position=self._position(ctx),
            identifier_position=self._position(ctx.nsIdentifier()).with_offset(start=Cursor(col=len(name) - len(last_namespace_identifier))),
            children=list(filter(None, [self.visit(content) for content in ctx.namespaceContent()])),
        )
        result._parsed_comment = parsed_comment
        for _ in range(self.current_namespace_stack_size.pop()):
            self.current_namespace.pop()
        return result


    def visitFilepath(self, ctx: IdlParser.FilepathContext) -> FileReference | None:
        node = ctx.FILEPATH()
        if not isinstance(node, ErrorNode):
            path = Path(node.getText()[1:-1])
            search_paths = [path, self.idl.parent / path] + [include_dir / path for include_dir in self.include_dirs]
            for search_path in search_paths:
                if search_path.exists() and not search_path.is_dir():
                    if search_path == self.idl:
                        self.errors.append(Parser.ParsingException(
                            f"Circular import detected: file {self.idl} directly references itself!",
                            position=self._position(ctx)
                        ))
                        return None
                    position = self._position(ctx)
                    path = FileReference(
                        path=search_path.absolute(),
                        position=position,
                        identifier_position=position.with_offset(start=Cursor(col=1), end=Cursor(col=-1))
                    )
                    self.file_imports.append(path)
                    return path
            self.errors.append(FileNotFoundException(path, self._position(ctx)))

    def visitExtern(self, ctx: IdlParser.ExternContext):
        extern_path = self.visit(ctx.filepath())
        if extern_path:
            try:
                self.resolver.load_external(extern_path.path)
            except InputParsingException as e:
                self.errors.append(e)


    def visitImportDef(self, ctx: IdlParser.ImportDefContext):
        import_path = self.visit(ctx.filepath())
        if import_path:
            try:
                imported_type_decls, type_refs, _, _, _ = Parser(
                    resolver=self.resolver,
                    targets=self.targets,
                    supported_target_keys=self.target_keys,
                    include_dirs=self.include_dirs,
                    default_deriving=self.default_deriving,
                    file_reader=self.file_reader,
                    idl=import_path.path,
                    position=self._position(ctx)
                ).parse()
                self.type_decls += imported_type_decls
                self.type_refs += type_refs
            except Parser.ParsingExceptionList as e:
                self.type_decls += e.type_decls
                self.type_refs += e.type_refs
                self.errors += e.items

    def _position(self, ctx) -> Position:
        return Position(
            start=Cursor(line=ctx.start.line - 1, col=ctx.start.column),
            end=Cursor(line=ctx.stop.line - 1, col=ctx.stop.column + len(ctx.stop.text)),
            file=self.idl
        )

    def _dependencies(self, type_refs: list[TypeReference]) -> list[TypeReference]:
        output: list[TypeReference] = []
        for type_ref in type_refs:
            output.append(type_ref)
            output += self._dependencies(type_ref.parameters)
        return output

    def parse(self) -> tuple[list[BaseType], list[TypeReference], list[FileReference], list[BaseField], list[BaseType | Namespace]]:
        ast: list[BaseType | Namespace] = []
        try:
            input_stream = InputStream(self.file_reader.read_idl(self.idl))
            lexer = IdlLexer(input_stream)
            lexer.removeErrorListeners()
            lexer.addErrorListener(Parser.ParsingErrorListener(self.idl, self.errors))
            stream = CommonTokenStream(lexer)
            parser = IdlParser(stream)
            parser.removeErrorListeners()
            parser.addErrorListener(Parser.ParsingErrorListener(self.idl, self.errors))
            tree = parser.idl()
            ast = self.visit(tree)
            for decl in self.type_decls + self.field_decls:
                if decl._parsed_comment:
                    ParserCommentProcessor(decl).render_tokens(*decl._parsed_comment)
            for type_ref in self.type_refs:
                if not type_ref.type_def:
                    try:
                        # TODO: maybe the setter in type_ref should raise the exception, and not the resolver?
                        # this way the behavior could be dynamic depending on the TypeReference class type (inversion of control)
                        type_ref.type_def = self.resolver.resolve(type_ref)
                    except Resolver.TypeResolvingException as e:
                        self.errors.append(e)
                    if type_ref.parameters and not type_ref.type_def.params:
                        self.errors.append(Parser.ParsingException(
                            f"Type '{type_ref.name}' does not accept generic parameters",
                            type_ref.position
                        ))
                    elif type_ref.parameters and len(type_ref.type_def.params) != len(type_ref.parameters):
                        expected_parameters = ", ".join(type_ref.type_def.params)
                        self.errors.append(Parser.ParsingException(
                            f"Invalid number of generic parameters given to '{type_ref.name}'. "
                            f"Expects {len(type_ref.type_def.params)} ({expected_parameters}), "
                            f"but {len(type_ref.parameters)} where given.",
                            type_ref.position
                        ))
            for target in self.targets:
                target.marshal(self.type_decls, self.field_decls)
            for decl in self.type_decls:
                if isinstance(decl, Record):
                    for field in decl.fields:
                        if field.type_ref.type_def:
                            if field.type_ref.type_def.primitive == BaseExternalType.Primitive.error:
                                self.errors.append(Parser.ParsingException(
                                    "Cannot assign an error as record field type",
                                    position=field.type_ref.position
                                ))
                            elif field.type_ref.type_def.primitive == BaseExternalType.Primitive.interface:
                                self.errors.append(Parser.ParsingException(
                                    "Cannot assign an interface as record field type",
                                    position=field.type_ref.position
                                ))
                        if Record.Deriving.ord in decl.deriving:
                            if field.type_ref.type_def and field.type_ref.type_def.primitive == BaseExternalType.Primitive.collection:
                                self.errors.append(Parser.ParsingException(
                                    "Cannot compare collections in 'ord' deriving",
                                    position=field.position
                                ))
                if isinstance(decl, Interface):
                    for method in decl.methods:
                        if method.return_type_ref and method.return_type_ref.type_def and method.return_type_ref.type_def.primitive == BaseExternalType.Primitive.error:
                            self.errors.append(Parser.ParsingException(
                                "Cannot return an error from a method",
                                position=method.return_type_ref.position
                            ))
                        if method.throwing is not None:
                            for type_ref in method.throwing:
                                if type_ref.type_def and type_ref.type_def.primitive != BaseExternalType.Primitive.error:
                                    self.errors.append(Parser.ParsingException(
                                        "Only errors can be thrown",
                                        position=type_ref.position
                                    ))
                        for parameter in method.parameters:
                            if parameter.type_ref.type_def and parameter.type_ref.type_def.primitive == BaseExternalType.Primitive.error:
                                self.errors.append(Parser.ParsingException(
                                    "Cannot pass an error type to a method",
                                    position=parameter.type_ref.position
                                ))
                if isinstance(decl, Function):
                    if decl.return_type_ref and decl.return_type_ref.type_def and decl.return_type_ref.type_def.primitive == BaseExternalType.Primitive.error:
                        self.errors.append(Parser.ParsingException(
                            "Cannot return an error type from a function",
                            position=decl.return_type_ref.position
                        ))
                    for parameter in decl.parameters:
                        if parameter.type_ref.type_def and parameter.type_ref.type_def.primitive == BaseExternalType.Primitive.error:
                            self.errors.append(Parser.ParsingException(
                                "Cannot pass an error type to a function",
                                position=parameter.type_ref.position
                            ))
                    if decl.throwing is not None:
                        for type_ref in decl.throwing:
                            if type_ref.type_def.primitive != BaseExternalType.Primitive.error:
                                self.errors.append(Parser.ParsingException(
                                    "Only errors can be thrown",
                                    position=type_ref.position
                                ))
        except FileNotFoundError as e:
            raise FileNotFoundException(Path(e.filename))
        except RecursionError:
            self.errors.append(Parser.ParsingException(
                f"Circular import detected: file {self.idl} indirectly imports itself!",
                self.position
            ))
        if self.errors:
            raise Parser.ParsingExceptionList(self.errors, self.type_decls, self.type_refs, self.file_imports, self.field_decls, ast)
        return self.type_decls, self.type_refs, self.file_imports, self.field_decls, ast
