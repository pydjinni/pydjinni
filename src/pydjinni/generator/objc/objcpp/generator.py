from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from .marshal import ObjcppMarshal
from pydjinni.generator.filters import quote, headers


class ObjcppGenerator(
    Generator,
    key="objcpp",
    marshal=ObjcppMarshal,
    writes_header=True,
    writes_source=True,
    support_lib_commons=True,
    filters=[quote, headers]
):
    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.h.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/enum.h.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.h.jinja2", type_def=type_def)
        self.write_source("source/record.mm.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.h.jinja2", type_def=type_def)
        self.write_source("source/interface.mm.jinja2", type_def=type_def)
