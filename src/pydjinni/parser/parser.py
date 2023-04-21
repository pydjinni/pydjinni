from pathlib import Path

import arpeggio
from arpeggio import PTNodeVisitor
from arpeggio import visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

from pydjinni.defs import IDL_GRAMMAR_PATH
from pydjinni.exceptions import FileNotFoundException, ApplicationException
from pydjinni.generator.marshal import Marshal
from .ast import *
from .resolver import Resolver


def unpack(list_input: []):
    return list_input[0] if list_input else None


class IdlParser:
    def __init__(self, resolver: Resolver, marshals: list[Marshal]):
        self.parser = ParserPEG(IDL_GRAMMAR_PATH.read_text(), root_rule_name="idl")
        self.resolver = resolver
        self.marshals = marshals

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

    class Visitor(PTNodeVisitor):
        def __init__(self, resolver: Resolver, marshals: list[Marshal], **kwargs):
            super().__init__(**kwargs)
            self.resolver = resolver
            self.marshals = marshals

        def visit_idl(self, node, children):
            return children[0:]

        def visit_type(self, node, children):
            datatype = unpack(children)
            self.resolver.register(datatype)
            return datatype

        def second_type(self, children):
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
            name = unpack(children.identifier)
            return Interface(
                name=name,
                position=node.position,
                comment=unpack(children.comment),
                methods=children.method
            )

        def visit_record(self, node, children):
            return Record(
                name=unpack(children.identifier),
                position=node.position,
                comment=unpack(children.comment),
                fields=children.field
            )

        def visit_identifier(self, node, children):
            return Identifier(node.value)

        def visit_datatype(self, node, children):
            return TypeReference(name=node.value, position=node.position)

        def second_datatype(self, children):
            self.resolver.resolve(children)

        def visit_item(self, node, children):
            return Enum.Item(
                name=unpack(children.identifier),
                position=node.position,
                comment=None
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
                return_type_ref=unpack(children.datatype),
                static=node[0] == 'static'
            )

        def second_method(self, children):
            for marshal in self.marshals:
                marshal.marshal(children)

        def visit_parameter(self, node, children):
            return Interface.Method.Parameter(
                name=unpack(children.identifier),
                position=node.position,
                type_ref=unpack(children.datatype)
            )

        def second_parameter(self, children):
            for marshal in self.marshals:
                marshal.marshal(children)

        def visit_field(self, node, children):
            return Record.Field(
                name=unpack(children.identifier),
                position=node.position,
                comment=unpack(children.comment),
                type_ref=unpack(children.datatype)
            )

        def second_field(self, children):
            for marshal in self.marshals:
                marshal.marshal(children)

        def visit_comment(self, node, children):
            return '\n'.join(children)

    def parse(self, idl: Path) -> list[BaseType]:
        """
        Parses the given input with `arpeggio`.

        - Creates the AST from the given IDL file.
        - Tries to resolve all type references.
        - Executes configured Marshals and extends the AST with the marshalled information.

        Args:
            idl: Path to the IDL file that should be parsed

        Returns:
            The parsed Abstract Syntax Tree (AST)

        Raises:
            IdlParser.ParsingException       : When the input could not be parsed.
            IdlParser.TypeResolvingException : When a referenced type cannot be found.
            IdlParser.DuplicateTypeException : When a type is re-declared.
            IdlParser.MarshalException       : When an error happened during marshalling.
        """
        try:
            parse_tree = self.parser.parse(idl.read_text())
            ast = visit_parse_tree(parse_tree, IdlParser.Visitor(self.resolver, self.marshals))
            return ast
        except FileNotFoundError as e:
            raise FileNotFoundException(idl)
        except Resolver.TypeResolvingException as e:
            line, col = self.parser.pos_to_linecol(e.position)
            context = self.parser.context(position=e.position)
            raise IdlParser.TypeResolvingException(idl, e.position, f"Unknown type '{e.type_reference.name}' at position ({line}, {col}) => '{context}' ")
        except Resolver.DuplicateTypeException as e:
            line, col = self.parser.pos_to_linecol(e.position)
            context = self.parser.context(position=e.position)
            raise IdlParser.DuplicateTypeException(idl, e.position, f"Type '{e.datatype.name}' at position ({line}, {col}) => '{context}' ")
        except arpeggio.NoMatch as e:
            raise IdlParser.ParsingException(idl, e.position, str(e)[:-1])
        except Marshal.MarshalException as e:
            raise IdlParser.MarshallingException(idl, e.input_def.position, f"'{e.input_def.name}' created {e}")
