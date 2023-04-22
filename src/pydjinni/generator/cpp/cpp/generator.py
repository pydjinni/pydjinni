from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from pydjinni.parser.base_models import BaseType
from .marshal import CppMarshal


class CppGenerator(Generator, key="cpp", marshal=CppMarshal):

    def write_header(self, template: str, type_def: BaseType):
        self.write(
            file=self.marshal.header_path() / type_def.cpp.header,
            template=template,
            type_def=type_def
        )

    def write_source(self, template: str, type_def: BaseType):
        self.write(
            file=self.marshal.source_path() / type_def.cpp.source,
            template=template,
            type_def=type_def
        )

    def generate_enum(self, type_def: Enum):
        self.write_header(template="header/enum.hpp.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header(template="header/flags.hpp.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header(template="header/record.hpp.jinja2", type_def=type_def)
        self.write_source(template="source/record.cpp.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header(template="header/interface.hpp.jinja2", type_def=type_def)
        self.write_source(template="source/interface.cpp.jinja2", type_def=type_def)
