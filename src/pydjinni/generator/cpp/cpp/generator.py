from pydjinni.generator.filters import header
from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from .marshal import CppMarshal


class CppGenerator(
    Generator,
    key="cpp",
    marshal=CppMarshal,
    writes_header=True,
    writes_source=True,
    support_lib_commons=True,
    filters=[header]
):

    def generate_enum(self, type_def: Enum):
        self.write_header(
            template="header/enum.hpp.jinja2",
            path=self.marshal.header_path() / type_def.cpp.header,
            type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header(
            template="header/flags.hpp.jinja2",
            path=self.marshal.header_path() / type_def.cpp.header,
            type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header(
            template="header/record.hpp.jinja2",
            path=self.marshal.header_path() / type_def.cpp.header,
            type_def=type_def
        )
        if type_def.constants:
            self.write_source(
                template="source/record.cpp.jinja2",
                path=self.marshal.source_path() / type_def.cpp.source,
                type_def=type_def
            )

    def generate_interface(self, type_def: Interface):
        self.write_header(
            template="header/interface.hpp.jinja2",
            path=self.marshal.header_path() / type_def.cpp.header,
            type_def=type_def
        )
        if type_def.constants:
            self.write_source(
                template="source/interface.cpp.jinja2",
                path=self.marshal.source_path() / type_def.cpp.source,
                type_def=type_def
            )
