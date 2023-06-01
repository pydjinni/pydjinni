from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import arpeggio
from arpeggio import PTNodeVisitor
from arpeggio import visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

from pydjinni.defs import IDL_GRAMMAR_PATH
from pydjinni.exceptions import FileNotFoundException, ApplicationException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.generator.marshal import Marshal
from .ast import *
from .resolver import Resolver


def unpack(list_input: []):
    return list_input[0] if list_input else None


class IdlParser(PTNodeVisitor):
    def __init__(self, resolver: Resolver, marshals: list[Marshal], targets: list[str], include_dirs: list[Path],
                 file_reader: FileReaderWriter, **kwargs):
        super().__init__(**kwargs)
        self.idl_parser = ParserPEG(IDL_GRAMMAR_PATH.read_text(), root_rule_name="idl")
        self.resolver = resolver
        self.marshals = marshals
        self.targets = targets
        self.file_reader = file_reader
        self.include_dirs = include_dirs

    class ParsingException(ApplicationException, code=150):
        """IDL Parsing error"""

        def __init__(self, idl: Path, position: int, message: str):
            super().__init__(message, file=idl)
            self.position = position

    class DuplicateTypeException(ParsingException, code=151):
        """The defined type already exists. IDL Parsing error"""

    class TypeResolvingException(ParsingException, code=152):
        """The referenced type could not be found. IDL Parsing error"""

    class MarshallingException(ParsingException, code=153):
        """Marshalling error"""

    class UnknownInterfaceTargetException(ParsingException, code=154):
        """Unknown interface target"""

    class RecursiveImport(ParsingException, code=155):
        """Recursive import detected"""

    @dataclass
    class VisitorUnknownInterfaceTargetException(Exception):
        """Exception raised when one of the given interface targets is not known to the parser"""
        target: str
        position: int

    @dataclass
    class VisitorMissingFieldException(Exception):
        """Exception raised when a const record assignment lacks a required keys"""
        field: str
        position: int

    @dataclass
    class VisitorUnknownFieldException(Exception):
        """Exception raised when a const record assignment defined a key that is unknown"""
        field: str
        position: int

    @dataclass
    class VisitorInvalidAssignmentException(Exception):
        """Exception raised when a const record assignment to an enum or flag defined an unknown value"""
        value: str
        position: int

    def visit_idl(self, node, children):
        imports = unpack(children.import_def) or []
        type_defs = children.type_def or []
        namespaced_type_defs = unpack(children.namespace) or []
        for type_def in type_defs + namespaced_type_defs:
            self.resolver.register(type_def)
        return imports + type_defs + namespaced_type_defs

    def visit_type_def(self, node, children):
        return unpack(children)

    def second_type_def(self, children):
        for marshal in self.marshals:
            marshal.marshal(children)

    def visit_enum(self, node, children):
        return Enum(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            items=children.item
        )

    def visit_flags(self, node, children):
        return Flags(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            flags=children.flag
        )

    def visit_flag(self, node, children):
        return Flags.Flag(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            all=len(node) == 4 and node[2] == 'all',
            none=len(node) == 4 and node[2] == 'none'
        )

    def second_flag(self, children):
        for marshal in self.marshals:
            marshal.marshal(children)

    def visit_interface(self, node, children):
        targets = unpack(children.targets) or self.targets
        return Interface(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            methods=children.method,
            targets=targets,
            constants=children.constant
        )

    def visit_record(self, node, children):
        return Record(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            fields=children.field,
            constants=children.constant
        )

    def visit_identifier(self, node, children):
        return Identifier(node.value)

    def visit_data_type(self, node, children):
        return TypeReference(name=node.value, position=node.position)

    def second_data_type(self, children):
        self.resolver.resolve(children)

    def visit_item(self, node, children):
        return Enum.Item(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment)
        )

    def second_item(self, children):
        for marshal in self.marshals:
            marshal.marshal(children)

    def visit_method(self, node, children):
        return Interface.Method(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            parameters=children.parameter,
            return_type_ref=unpack(children.data_type),
            static=node[0] == 'static'
        )

    def second_method(self, children):
        for marshal in self.marshals:
            marshal.marshal(children)

    def visit_parameter(self, node, children):
        return Interface.Method.Parameter(
            name=unpack(children.identifier),
            comment=unpack(children.comment),
            position=node.position,
            type_ref=unpack(children.data_type)
        )

    def visit_targets(self, node, children):
        includes = []
        excludes = []
        for child in children:
            if child.startswith('+'):
                includes.append(child[1:])
            else:
                excludes.append(child[1:])
        if not includes:
            includes = self.targets

        targets = [include for include in includes if include not in excludes]
        for target in targets:
            if target not in self.targets:
                raise IdlParser.VisitorUnknownInterfaceTargetException(target=target, position=node.position)
        return targets

    def second_parameter(self, children):
        for marshal in self.marshals:
            marshal.marshal(children)

    def visit_field(self, node, children):
        return Record.Field(
            name=unpack(children.identifier),
            position=node.position,
            comment=unpack(children.comment),
            type_ref=unpack(children.data_type)
        )

    def second_field(self, children):
        for marshal in self.marshals:
            marshal.marshal(children)

    def visit_comment(self, node, children):
        return [child[1:] for child in children]

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
        unpack(children.identifier), unpack(children.value)
        return Assignment(
            key=unpack(children.identifier),
            position=node.position,
            value=unpack(children.value)
        )

    def visit_object(self, node, children):
        return children

    def visit_constant(self, node, children):
        return Constant(
            name=unpack(children.identifier),
            type_ref=unpack(children.data_type),
            value=unpack(children.value),
            position=node.position
        )

    def second_constant(self, children):
        type_def = children.type_ref.type_def
        match type_def:
            case BaseExternalType():
                primitive = type_def.primitive
                value = children.value
                if not (type_def.primitive and (
                        (primitive == BaseExternalType.Primitive.int and type(value) == int) or
                        (primitive == BaseExternalType.Primitive.float and type(value) == float) or
                        (primitive == BaseExternalType.Primitive.string and type(value) == str) or
                        (primitive == BaseExternalType.Primitive.bool and type(value) == bool))):
                    raise IdlParser.VisitorInvalidAssignmentException(str(value), children.position)
            case Flags() | Enum():
                fields = [item.name for item in (type_def.items or type_def.flags)]
                if children.value not in fields:
                    raise IdlParser.VisitorInvalidAssignmentException(str(children.value), children.position)
            case Record():
                fields = type_def.fields
                assignment_keys = [assignment.key for assignment in children.value]
                record_keys = [field.name for field in fields]
                for assignment in children.value:
                    if assignment.key not in record_keys:
                        raise IdlParser.VisitorUnknownFieldException(assignment.key, assignment.position)
                for field in fields:
                    if field.name not in assignment_keys:
                        raise IdlParser.VisitorMissingFieldException(field.name, children.position)

    def visit_import_def(self, node, children):
        ast = self.parse(unpack(children.filepath), node.position)
        return ast

    def visit_extern(self, node, children):
        self.resolver.load_external(unpack(children.filepath))

    def visit_namespace(self, node, children):
        namespaced_type_defs = unpack(children.namespace) or []
        for type_def in children.type_def + namespaced_type_defs:
            type_def.namespace = children.identifier + type_def.namespace
        return children.type_def + namespaced_type_defs

    def _get_context(self, position) -> tuple[int, int, str]:
        line, col = self.idl_parser.pos_to_linecol(position)
        context = self.idl_parser.context(position=position)
        return line, col, context

    def parse(self, idl: Path, position: int = 0) -> list[BaseType]:
        """
        Parses the given input with `arpeggio`.

        - Creates the AST from the given IDL file.
        - Tries to resolve all type references.
        - Executes configured Marshals and extends the AST with the marshalled information.

        Args:
            idl: Path to the IDL file that should be parsed
            position: The position of the @import statement, if the method is called recursively by an import

        Returns:
            The parsed Abstract Syntax Tree (AST)

        Raises:
            IdlParser.ParsingException       : When the input could not be parsed.
            IdlParser.TypeResolvingException : When a referenced type cannot be found.
            IdlParser.DuplicateTypeException : When a type is re-declared.
            IdlParser.MarshalException       : When an error happened during marshalling.
        """
        try:
            parse_tree = self.idl_parser.parse(self.file_reader.read_idl(idl))
            return visit_parse_tree(parse_tree, self)
        except FileNotFoundError as e:
            raise FileNotFoundException(idl)
        except Resolver.TypeResolvingException as e:
            line, col, context = self._get_context(e.position)
            raise IdlParser.TypeResolvingException(
                idl,
                e.position,
                f"Unknown type '{e.type_reference.name}' at position ({line}, {col}) => '{context}' "
            )
        except Resolver.DuplicateTypeException as e:
            line, col, context = self._get_context(e.position)
            raise IdlParser.DuplicateTypeException(
                idl,
                e.position,
                f"Type '{e.datatype.name}' at position ({line}, {col}) => '{context}' "
            )
        except arpeggio.NoMatch as e:
            raise IdlParser.ParsingException(idl, e.position, str(e)[:-1])
        except Marshal.MarshalException as e:
            raise IdlParser.MarshallingException(idl, e.input_def.position, f"'{e.input_def.name}' created {e}")
        except IdlParser.VisitorUnknownInterfaceTargetException as e:
            line, col, context = self._get_context(e.position)
            raise IdlParser.UnknownInterfaceTargetException(
                idl,
                e.position,
                f"'{e.target}' at position ({line}, {col}) => '{context}' "
            )
        except IdlParser.VisitorMissingFieldException as e:
            line, col, context = self._get_context(e.position)
            raise IdlParser.ParsingException(
                idl, e.position,
                f"Missing field '{e.field}' in constant assignment at position ({line}, {col}) => '{context}'"
            )
        except IdlParser.VisitorUnknownFieldException as e:
            line, col, context = self._get_context(e.position)
            raise IdlParser.ParsingException(
                idl, e.position,
                f"Unknown field '{e.field}' defined in constant assignment at position ({line}, {col}) => '{context}'"
            )
        except IdlParser.VisitorInvalidAssignmentException as e:
            line, col, context = self._get_context(e.position)
            raise IdlParser.ParsingException(
                idl, e.position,
                f"Invalid value '{e.value}' assigned to const at position ({line}, {col}) => '{context}'"
            )
        except RecursionError:
            line, col, context = self._get_context(position)
            raise IdlParser.RecursiveImport(
                idl, position,
                f"file imports itself at position ({line}, {col}) => '{context}'"
            )
