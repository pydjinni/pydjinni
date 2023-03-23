import arpeggio
from arpeggio.cleanpeg import ParserPEG
from arpeggio import visit_parse_tree
from logging import Logger
from pydjinni.defs import IDL_GRAMMAR_PATH
from pydjinni.exceptions import FileNotFoundException, ParsingException
from arpeggio import PTNodeVisitor
from .ast import *
from .resolver import Resolver
from rich.pretty import pretty_repr

def unpack(list_input: []):
    return list_input[0] if list_input else None


class IdlParser:
    def __init__(self, logger: Logger, resolver: Resolver):
        self.logger = logger
        self.parser = ParserPEG(IDL_GRAMMAR_PATH.read_text(), root_rule_name="idl")
        self.resolver = resolver
    class Visitor(PTNodeVisitor):
        def __init__(self, logger: Logger, resolver: Resolver, **kwargs):
            super().__init__(**kwargs)
            self.logger = logger
            self.resolver = resolver

        def visit_idl(self, node, children):
            return children[0:]

        def visit_type(self, node, children):
            datatype = unpack(children)
            self.resolver.register(datatype)
            return datatype

        def visit_enum(self, node, children):
            return Enum(
                name=unpack(children.identifier),
                metadata=Metadata(
                    position=node.position,
                    position_end=node.position_end
                ),
                comment=unpack(children.comment),
                cpp=None,
                java=None,
                jni=None,
                objc=None,
                objcpp=None,
                items=children.item
            )

        def visit_flags(self, node, children):
            begin = node.position if node[0].rule_name != "comment" else node[1].position
            return Flags(
                name=unpack(children.identifier),
                metadata=Metadata(
                    position=begin,
                    position_end=node.position_end
                ),
                comment=unpack(children.comment),
                cpp=None,
                java=None,
                jni=None,
                objc=None,
                objcpp=None,
                flags=children.flag
            )

        def visit_flag(self, node, children):
            return Flags.Flag(
                name=unpack(children.identifier),
                comment=unpack(children.comment),
                all=len(node) == 4 and node[2] == 'all',
                none=len(node) == 4 and node[2] == 'none'
            )

        def visit_interface(self, node, children):
            return Interface(
                name=unpack(children.identifier),
                metadata=Metadata(
                    position=node.position,
                    position_end=node.position_end
                ),
                comment=unpack(children.comment),
                cpp=None,
                java=None,
                jni=None,
                objc=None,
                objcpp=None,
                methods=children.method
            )

        def visit_record(self, node, children):
            return Record(
                name=unpack(children.identifier),
                metadata=Metadata(
                    position=node.position,
                    position_end=node.position_end
                ),
                comment=unpack(children.comment),
                cpp=None,
                java=None,
                jni=None,
                objc=None,
                objcpp=None,
                fields=children.field
            )

        def visit_identifier(self, node, children):
            return node.value

        def visit_datatype(self, node, children):
            return TypeReference(
                metadata=Metadata(
                    position=node.position,
                    position_end=node.position_end
                ),
                name=node.value)

        def second_datatype(self, children):
            self.resolver.resolve(children)

        def visit_item(self, node, children):
            return Enum.Item(
                name=unpack(children.identifier),
                comment=None
            )

        def visit_method(self, node, children):
            return Interface.Method(
                name=unpack(children.identifier),
                comment=unpack(children.comment),
                parameters=children.parameter,
                return_type_reference=unpack(children.datatype),
                static=node[0] == 'static'
            )

        def visit_parameter(self, node, children):
            return Interface.Method.Parameter(
                name=unpack(children.identifier),
                type_reference=unpack(children.datatype)
            )

        def visit_field(self, node, children):
            return Record.Field(
                name=unpack(children.identifier),
                comment=unpack(children.comment),
                type_reference=unpack(children.datatype)
            )

        def visit_comment(self, node, children):
            return '\n'.join(children)

    def parse(self, idl: Path):
        try:
            self.logger.debug(f"parsing the idl {idl.absolute()}:")
            parse_tree = self.parser.parse(idl.read_text())
            self.logger.debug(parse_tree.tree_str())
            ast = visit_parse_tree(parse_tree, IdlParser.Visitor(self.logger, self.resolver))
            self.logger.debug(f"resulting ast:")
            self.logger.debug(pretty_repr(ast))
            return ast
        except FileNotFoundError as e:
            raise FileNotFoundException(f"IDL file can not be found: '{idl}'")
        except Resolver.TypeResolvingException as e:
            line, col = self.parser.pos_to_linecol(e.type_reference.metadata.position)
            context = self.parser.context(position=e.type_reference.metadata.position)
            raise ParsingException(f"Error parsing IDL file '{idl}': Unknown type '{e.type_reference.name}' at position ({line}, {col}) => '{context}' ")
        except Resolver.DuplicateTypeException as e:
            line, col = self.parser.pos_to_linecol(e.datatype.metadata.position)
            context = self.parser.context(position=e.datatype.metadata.position)
            raise ParsingException(f"Error parsing IDL file '{idl}': Type '{e.datatype.name}' at position ({line}, {col}) already exists => '{context}' ")
        except arpeggio.NoMatch as e:
            raise ParsingException(f"Error parsing IDL file '{idl}': {e}")


