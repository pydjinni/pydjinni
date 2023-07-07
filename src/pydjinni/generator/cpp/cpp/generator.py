from pydjinni.generator.filters import headers, quote
from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from .marshal import CppMarshal
from .filters import needs_optional


class CppGenerator(
    Generator,
    key="cpp",
    marshal=CppMarshal,
    writes_header=True,
    writes_source=True,
    support_lib_commons=True,
    filters=[quote, headers, needs_optional]
):

    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.hpp.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/flags.hpp.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.hpp.jinja2", type_def=type_def)
        if type_def.constants:
            self.write_source("source/record.cpp.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.hpp.jinja2", type_def=type_def)
        if type_def.constants:
            self.write_source("source/interface.cpp.jinja2", type_def=type_def)
