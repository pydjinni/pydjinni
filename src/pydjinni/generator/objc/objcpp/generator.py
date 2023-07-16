from pydjinni.generator.generator import Generator
from pydjinni.parser.base_models import BaseType, BaseField, SymbolicConstantField
from .config import ObjcppConfig
from .type import ObjcppExternalType, ObjcppBaseType, ObjcppBaseField, ObjcppSymbolicConstantField
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from pydjinni.generator.filters import quote, headers
from .external_types import external_types


class ObjcppGenerator(Generator):
    key = "objcpp"
    config_model = ObjcppConfig
    external_type_model = ObjcppExternalType
    external_types = external_types
    marshal_models = {
        BaseType: ObjcppBaseType,
        BaseField: ObjcppBaseField,
        SymbolicConstantField: ObjcppSymbolicConstantField
    }
    writes_header = True
    writes_source = True
    support_lib_commons = True
    filters = [quote, headers]

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
