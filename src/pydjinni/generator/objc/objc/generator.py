from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from pydjinni.parser.base_models import BaseType
from .marshal import ObjcMarshal
from pydjinni.generator.filters import quote, headers


class ObjcGenerator(
    Generator,
    key="objc",
    marshal=ObjcMarshal,
    writes_header=True,
    writes_source=True,
    filters=[quote, headers]
):

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
            type_def=type_def
        )
        self.write_source(
            template="source/record.m.jinja2",
            path=self.marshal.source_path() / type_def.objc.source,
            type_def=type_def
        )

    def generate_interface(self, type_def: Interface):
        self.write_header(
            template="header/interface.h.jinja2",
            path=self.marshal.header_path() / type_def.objc.header,
            type_def=type_def)
        if type_def.constants:
            self.write_source(
                template="source/interface.m.jinja2",
                path=self.marshal.source_path() / type_def.objc.source,
                type_def=type_def
            )

    def generate_bridging_header(self, ast: list[BaseType]):
        if self.marshal.config.swift.bridging_header:
            path = self.marshal.header_path() / self.marshal.config.swift.bridging_header
            self.write_header(
                template="header/bridging_header.h.jinja2",
                path=path,
                ast=ast
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_bridging_header(ast)
