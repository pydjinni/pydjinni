from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from pydjinni.parser.base_models import BaseType
from .marshal import ObjcMarshal


class ObjcGenerator(Generator, key="objc", marshal=ObjcMarshal, writes_header=True):

    def generate_enum(self, type_def: Enum):
        self.write_header(
            template="header/enum.h.jinja2",
            path=self.marshal.header_path() / type_def.objc.header,
            type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header(
            template="header/flags.h.jinja2",
            path=self.marshal.header_path() / type_def.objc.header,
            type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header(
            template="header/record.h.jinja2",
            path=self.marshal.header_path() / type_def.objc.header,
            type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header(
            template="header/interface.h.jinja2",
            path=self.marshal.header_path() / type_def.objc.header,
            type_def=type_def)

    def generate_bridging_header(self, ast: list[BaseType]):
        if self.marshal.config.swift.bridging_header:
            path = self.marshal.header_path() / self.marshal.config.swift.bridging_header
            self.write_header(
                template="header/bridging_header.h.jinja2",
                path=path,
                ast=ast
            )

    def generate(self, ast: list[BaseType]):
        super().generate(ast)
        self.generate_bridging_header(ast)
