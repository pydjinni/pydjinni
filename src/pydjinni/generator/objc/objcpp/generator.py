from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from pydjinni.parser.base_models import BaseType
from .marshal import ObjcppMarshal
from pydjinni.generator.filters import header


class ObjcppGenerator(
    Generator,
    key="objcpp",
    marshal=ObjcppMarshal,
    writes_header=True,
    writes_source=True,
    support_lib_commons=True,
    filters=[header]
):
    def generate_enum(self, type_def: Enum):
        self.write_header(
            template="header/enum.h.jinja2",
            path=self.marshal.header_path() / type_def.objcpp.header,
            type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header(
            template="header/flags.h.jinja2",
            path=self.marshal.header_path() / type_def.objcpp.header,
            type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header(
            template="header/record.h.jinja2",
            path=self.marshal.header_path() / type_def.objcpp.header,
            type_def=type_def)
        self.write_source(
            template="source/record.mm.jinja2",
            path=self.marshal.source_path() / type_def.objcpp.source,
            type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header(
            template="header/interface.h.jinja2",
            path=self.marshal.header_path() / type_def.objcpp.header,
            type_def=type_def)
        self.write_source(
            template="source/interface.mm.jinja2",
            path=self.marshal.source_path() / type_def.objcpp.source,
            type_def=type_def)
