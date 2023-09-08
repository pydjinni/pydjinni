from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import (
    Interface,
    Record,
    Flags,
    Enum,
    Parameter, Function
)
from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    SymbolicConstantField
)
from .config import ObjcConfig
from pydjinni.generator.filters import quote, headers
from .type import (
    ObjcExternalType,
    ObjcBaseType,
    ObjcBaseField,
    ObjcInterface,
    ObjcSymbolicConstantField,
    ObjcRecord,
    ObjcParameter,
    ObjcFunction
)
from .external_types import external_types


class ObjcGenerator(Generator):
    key = "objc"
    config_model = ObjcConfig
    external_type_model = ObjcExternalType
    external_types = external_types
    marshal_models = {
        BaseType: ObjcBaseType,
        BaseField: ObjcBaseField,
        Interface: ObjcInterface,
        Interface.Method: ObjcInterface.ObjcMethod,
        Interface.Property: ObjcInterface.ObjcProperty,
        Function: ObjcFunction,
        SymbolicConstantField: ObjcSymbolicConstantField,
        Record: ObjcRecord,
        Record.Field: ObjcRecord.ObjcField,
        Parameter: ObjcParameter
    }
    writes_header = True
    writes_source = True
    filters = [quote, headers]

    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.h.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/flags.h.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.h.jinja2", type_def=type_def)
        self.write_source("source/record.m.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.h.jinja2", type_def=type_def)

    def generate_function(self, type_def: Function):
        pass

    def generate_bridging_header(self, ast: list[BaseType]):
        if self.config.swift.bridging_header:
            self.write_header(
                template="header/bridging_header.h.jinja2",
                filename=self.config.swift.bridging_header,
                ast=ast
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_bridging_header(ast)
