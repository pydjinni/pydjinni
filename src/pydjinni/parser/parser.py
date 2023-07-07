from __future__ import annotations

from pathlib import Path

import arpeggio
from arpeggio import PTNodeVisitor
from arpeggio import visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

from pydjinni.defs import IDL_GRAMMAR_PATH
from pydjinni.exceptions import FileNotFoundException, ApplicationException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.generator.cpp.cpp.generator import CppGenerator
from .ast import *
from .base_models import Assignment, Constant, BaseExternalType, ObjectValue
from .identifier import Identifier
from .resolver import Resolver
from pydjinni.generator.marshal import Marshal


def unpack(list_input: []):
    return list_input[0] if list_input else None


class IdlParser(PTNodeVisitor):
    def __init__(
            self,
            resolver: Resolver,
            targets: list[str],
            include_dirs: list[Path],
            default_deriving: set[Record.Deriving],
            file_reader: FileReaderWriter,
            marshals: list[Marshal],
            idl: Path,
            position: int = 0,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.idl_parser = ParserPEG(IDL_GRAMMAR_PATH.read_text(), root_rule_name="idl")
        self.resolver = resolver
        self.targets = targets
        self.file_reader = file_reader
        self.include_dirs = include_dirs
        self.default_deriving = default_deriving
        self.marshals = marshals
        self.idl = idl
        self.position = position
        self.type_defs: list[BaseType] = []
        self.current_namespace: list[Identifier] = []
        self.current_namespace_stack_size: list[int] = []

    class ParsingException(ApplicationException, code=150):
        """IDL Parsing error"""

        def __init__(self, idl: Path, line: int, col: int, context: str, message: str = ""):
            super().__init__(f"{message} at position ({line}, {col}) => '{context}'", file=idl)
            self.line = line
            self.col = col
            self.message = message

    class DuplicateTypeException(ParsingException, code=151):
        """The defined type already exists. IDL Parsing error"""

    class TypeResolvingException(ParsingException, code=152):
        """The referenced type could not be resolved. IDL Parsing error"""

    class StaticNotAllowedException(ParsingException):
        """methods are only allowed to be static on 'cpp' interfaces"""

    class StaticAndConstException(ParsingException):
        """method cannot be both static and const"""

    class UnknownInterfaceTargetException(ParsingException, code=154):
        """Unknown interface target"""

    class RecursiveImport(ParsingException, code=155):
        """Recursive import detected"""

    class MissingFieldException(ParsingException):
        """Exception raised when a const record assignment lacks a required keys"""

    class UnknownFieldException(ParsingException):
        """Exception raised when a const record assignment defined a key that is unknown"""

    class InvalidAssignmentException(ParsingException):
        """Exception raised when a const record assignment defined an unknown value"""

    def visit_type_def(self, node, children) -> BaseType:
        type_def = unpack(children)
        self.resolver.register(type_def)
        self.type_defs.append(type_def)
        return type_def

    def visit_class_type_def(self, node, children):
        type_def: BaseClassType = unpack(children)
        type_def.dependencies += self._dependencies([constant.type_ref for constant in type_def.constants])
        return type_def

    def visit_enum(self, node, children):
        enum = Enum(
            name=unpack(children.identifier),
            position=node.position,
            items=children.item,
            namespace=self.current_namespace
        )
        if children.comment:
            enum.comment = unpack(children.comment)
        return enum

    def visit_flags(self, node, children):
        flags = Flags(
            name=unpack(children.identifier),
            position=node.position,
            flags=children.flag,
            namespace=self.current_namespace
        )
        if children.comment:
            flags.comment = unpack(children.comment)
        return flags

    def visit_flag(self, node, children):
        all = unpack(children.flag_modifier) == 'all' if children.flag_modifier else False
        none = unpack(children.flag_modifier) == 'none' if children.flag_modifier else False
        return Flags.Flag(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            all=all,
            none=none
        )

    def visit_flag_modifier(self, node, children):
        return children[0]

    def visit_interface(self, node, children):
        targets: list[str] = unpack(children.targets) or self.targets
        main: bool = 'main' in children.results
        methods: list[Interface.Method] = children.method
        properties: list[Interface.Property] = children.property
        dependencies: list[TypeReference] = []

        if main and targets != [CppGenerator.key]:
            raise IdlParser.ParsingException(
                self.idl, *self._get_context(node.position),
                message="a 'main' interface can only be implemented in C++"
            )
        for method in methods:
            if CppGenerator.key not in targets and method.static:
                raise IdlParser.StaticNotAllowedException(self.idl, *self._get_context(method.position))
            for param in method.parameters:
                dependencies.append(param.type_ref)
            if method.return_type_ref:
                dependencies.append(method.return_type_ref)
        for property_def in properties:
            dependencies.append(property_def.type_ref)
        interface = Interface(
            name=unpack(children.identifier),
            position=node.position,
            methods=methods,
            targets=targets,
            constants=children.constant,
            properties=properties,
            main=main,
            namespace=self.current_namespace,
            dependencies=self._dependencies(dependencies)
        )
        if children.comment:
            interface.comment = unpack(children.comment)
        return interface

    def visit_named_function(self, node, children):
        function = unpack(children.function)
        function.name = unpack(children.identifier)
        if children.comment:
            function.comment = unpack(children.comment)
        function.position = node.position
        return function

    def visit_function(self, node, children):
        targets: list[str] = unpack(children.targets) or self.targets
        return Function(
            name="<anonymous>",
            position=node.position,
            parameters=children.parameter,
            targets=targets,
            namespace=self.current_namespace,
            return_type_ref=unpack(children.data_type)
        )

    def visit_deriving(self, node, children):
        return set(children.declaration)

    def visit_declaration(self, node, children):
        try:
            return Record.Deriving(node.value)
        except ValueError:
            raise IdlParser.ParsingException(
                self.idl,
                *self._get_context(node.position),
                message=f"{node.value} is not a valid record deriving")

    def visit_record(self, node, children):
        targets = unpack(children.targets) or []
        fields: list[Record.Field] = children.field
        deriving = unpack(children.deriving) or set()
        record = Record(
            name=unpack(children.identifier),
            position=node.position,
            fields=fields,
            targets=targets,
            constants=children.constant,
            namespace=self.current_namespace,
            dependencies=self._dependencies([field.type_ref for field in fields]),
            deriving=deriving | self.default_deriving
        )
        if children.comment:
            record.comment = unpack(children.comment)
        return record

    def visit_data_type(self, node, children):
        if children.function:
            type_def = unpack(children.function)
            self.type_defs.append(type_def)
            type_ref = TypeReference(
                name="<function>",
                position=node.position,
                type_def=type_def,
                namespace=self.current_namespace
            )
        else:
            parameters = children.data_type or []
            type_ref = TypeReference(
                name=str(node[0]),
                parameters=parameters,
                position=node.position,
                namespace=self.current_namespace,
                optional='optional' in children.results
            )
        return type_ref

    def second_data_type(self, type_ref: TypeReference):
        if not type_ref.type_def:
            self.resolver.resolve(type_ref)
            if type_ref.parameters and not type_ref.type_def.params:
                raise IdlParser.TypeResolvingException(
                    self.idl,
                    *self._get_context(type_ref.position),
                    message=f"Type '{type_ref.name}' does not accept generic parameters")
            elif type_ref.parameters and len(type_ref.type_def.params) != len(type_ref.parameters):
                expected_parameters = ", ".join(type_ref.type_def.params)
                raise IdlParser.TypeResolvingException(
                    self.idl,
                    *self._get_context(type_ref.position),
                    message=f"Invalid number of generic parameters given to '{type_ref.name}'. "
                            f"Expects {len(type_ref.type_def.params)} ({expected_parameters}), but {len(type_ref.parameters)} where given.")

    def visit_item(self, node, children):
        return Enum.Item(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment)
        )

    def visit_method(self, node, children):
        static = 'static' in children
        const = 'const' in children
        if static and const:
            raise IdlParser.StaticAndConstException(self.idl, *self._get_context(node.position))
        return Interface.Method(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            parameters=children.parameter,
            return_type_ref=unpack(children.data_type),
            static='static' in children,
            const='const' in children,
        )

    def visit_property(self, node, children):
        return Interface.Property(
            name=unpack(children.identifier),
            type_ref=unpack(children.data_type),
            comment=unpack(children.comment),
            position=node.position
        )

    def visit_parameter(self, node, children):
        return Parameter(
            name=unpack(children.identifier),
            comment=unpack(children.comment),
            position=node.position,
            type_ref=unpack(children.data_type)
        )

    def visit_targets(self, node, children):
        includes = []
        excludes = []
        for item in children:
            if item.startswith('+'):
                includes.append(item[1:])
            else:
                excludes.append(item[1:])
        if (not includes) and excludes:
            includes = self.targets

        targets = [include for include in includes if include not in excludes]
        for target in targets:
            if target not in self.targets:
                raise IdlParser.UnknownInterfaceTargetException(
                    self.idl,
                    *self._get_context(node.position),
                    message=f"'{target}'"
                )
        return targets

    def visit_field(self, node, children):
        return Record.Field(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            type_ref=unpack(children.data_type)
        )

    def second_field(self, field: Record.Field):
        if isinstance(field.type_ref.type_def, Function):
            raise IdlParser.ParsingException(
                self.idl,
                *self._get_context(field.position),
                message="functions are not allowed as record field type."
            )

    def visit_comment(self, node, children):
        return "\n".join([child[1:] for child in children])

    def visit_filepath(self, node, children):
        path = Path(node.value[1:-1])
        search_paths = [path] + [include_dir / path for include_dir in self.include_dirs]
        for search_path in search_paths:
            if search_path.exists():
                return search_path
        raise FileNotFoundException(path)

    def visit_string(self, node, children) -> str:
        return node.value[1:-1]

    def visit_integer(self, node, children) -> int:
        return int(node.value)

    def visit_float(self, node, children) -> float:
        return float(node.value)

    def visit_bool(self, node, children) -> bool:
        return node.value == "True"

    def visit_assignment(self, node, children):
        return Assignment(
            key=unpack(children.identifier),
            position=node.position,
            value=unpack(children.value)
        )

    def visit_value(self, node, children):
        return children[0]

    def visit_object(self, node, children):
        return ObjectValue(
            assignments={assignment.key: assignment for assignment in children.assignment}
        )

    def visit_constant(self, node, children) -> Constant:
        return Constant(
            name=unpack(children.identifier),
            type_ref=unpack(children.data_type),
            value=unpack(children.value),
            position=node.position,
            comment=unpack(children.comment)
        )

    def second_constant(self, constant: Constant):
        if isinstance(constant.type_ref.type_def, Function):
            raise IdlParser.ParsingException(
                self.idl,
                *self._get_context(constant.position),
                message="functions are not allowed as constant field type."
            )
        self._check_const_assignment(constant.name, constant.type_ref.type_def, constant.value, constant.position)

    def _dependencies(self, type_refs: list[TypeReference]) -> list[TypeReference]:
        output: list[TypeReference] = []
        for type_ref in type_refs:
            output.append(type_ref)
            output += self._dependencies(type_ref.parameters)
        return output

    def _check_const_assignment(self, name, type_def, value, position):
        match type_def:
            case Flags() | Enum():
                fields = [item.name for item in (type_def.items or type_def.flags)]
                if value not in fields:
                    raise IdlParser.InvalidAssignmentException(
                        self.idl,
                        *self._get_context(position),
                        message=f"Invalid value '{str(value)}' assigned to const"
                    )
            case Record():
                fields = type_def.fields
                if type(value) is ObjectValue:
                    record_keys = [field.name for field in fields]
                    for assignment in value.assignments.values():
                        if assignment.key not in record_keys:
                            raise IdlParser.UnknownFieldException(
                                self.idl,
                                *self._get_context(assignment.position),
                                message=f"Unknown field '{assignment.key}' defined in constant assignment"
                            )
                    for field in fields:
                        if field.name in value.assignments:
                            self._check_const_assignment(
                                field.name,
                                field.type_ref.type_def,
                                value.assignments[field.name].value,
                                value.assignments[field.name].position
                            )
                        else:
                            raise IdlParser.MissingFieldException(
                                self.idl,
                                *self._get_context(position),
                                message=f"Missing field '{field.name}' in constant assignment"
                            )

                else:
                    raise IdlParser.InvalidAssignmentException(
                        self.idl,
                        *self._get_context(position),
                        message=f"Invalid primitive value '{str(value)}' assigned to const record type '{type_def.name}'"
                    )

            case BaseExternalType():
                primitive = type_def.primitive
                if not ((primitive == BaseExternalType.Primitive.int and type(value) == int) or
                        (primitive == BaseExternalType.Primitive.float and type(value) == float) or
                        (primitive == BaseExternalType.Primitive.double and type(value) == float) or
                        (primitive == BaseExternalType.Primitive.string and type(value) == str) or
                        (primitive == BaseExternalType.Primitive.bool and type(value) == bool)):
                    if type(value) == str:
                        value_description = f'string value "{value}"'
                    elif type(value) in [int, float, bool]:
                        value_description = f"primitive value '{value}'"
                    else:
                        value_description = f"value"
                    raise IdlParser.InvalidAssignmentException(
                        self.idl,
                        *self._get_context(position),
                        message=f"Invalid {value_description} assigned to const '{name}' of type '{type_def.name}'"
                    )
    def visit_import_def(self, node, children):
        ast = IdlParser(
            resolver=self.resolver,
            targets=self.targets,
            include_dirs=self.include_dirs,
            default_deriving=self.default_deriving,
            file_reader=self.file_reader,
            marshals=self.marshals,
            idl=unpack(children.filepath),
            position=node.position).parse()
        self.type_defs += ast
        return ast

    def visit_extern(self, node, children):
        self.resolver.load_external(unpack(children.filepath))

    def visit_begin_namespace(self, node, children):
        self.current_namespace += children.identifier
        self.current_namespace_stack_size.append(len(children.identifier))

    def visit_end_namespace(self, node, children):
        for _ in range(self.current_namespace_stack_size.pop()):
            self.current_namespace.pop()


    def _get_context(self, position) -> tuple[int, int, str]:
        line, col = self.idl_parser.pos_to_linecol(position)
        context = self.idl_parser.context(position=position)
        return line, col, context

    def parse(self) -> list[BaseType]:
        """
        Parses the given input with `arpeggio`.

        - Creates the AST from the given IDL file.
        - Tries to resolve all type references.

        Args:
            idl: Path to the IDL file that should be parsed
            position: The position of the @import statement, if the method is called recursively by an import

        Returns:
            The parsed Abstract Syntax Tree (AST)

        Raises:
            IdlParser.ParsingException       : When the input could not be parsed.
            IdlParser.TypeResolvingException : When a referenced type cannot be found.
            IdlParser.DuplicateTypeException : When a type is re-declared.
        """
        try:
            parse_tree = self.idl_parser.parse(self.file_reader.read_idl(self.idl))
            visit_parse_tree(parse_tree, self)
            for marshal in self.marshals:
                marshal.marshal(self.type_defs)
            return self.type_defs
        except FileNotFoundError as e:
            raise FileNotFoundException(self.idl)
        except Resolver.TypeResolvingException as e:
            raise IdlParser.TypeResolvingException(
                self.idl,
                *self._get_context(e.position),
                message=f"Unknown type '{e.type_reference.name}'"
            )
        except Resolver.DuplicateTypeException as e:
            raise IdlParser.DuplicateTypeException(
                self.idl,
                *self._get_context(e.position),
                message=f"Type '{e.datatype.name}' has been redefined"
            )
        except arpeggio.NoMatch as e:
            e.eval_attrs()
            raise IdlParser.ParsingException(self.idl, *self._get_context(e.position), message=e.message)
        except RecursionError:
            raise IdlParser.RecursiveImport(
                self.idl,
                *self._get_context(self.position),
                message=f"file imports itself"
            )
        except Marshal.MarshalException as e:
            raise IdlParser.ParsingException(self.idl, *self._get_context(e.input_def.position), message=str(e))
