from pydjinni.generator.filters import headers, quote
from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import (
    Interface,
    Record,
    Flags,
    Enum,
    Function,
    Parameter
)
from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    SymbolicConstantField,
    Constant
)
from .config import CppConfig
from .external_types import external_types
from .filters import needs_optional
from .type import (
    CppExternalType,
    CppBaseType,
    CppInterface,
    CppRecord,
    CppFunction,
    CppBaseField,
    CppSymbolicConstantField,
    CppParameter,
    CppConstant
)


class CppGenerator(Generator):
    key = "cpp"
    config_model = CppConfig
    external_type_model = CppExternalType
    external_types = external_types
    marshal_models = {
        BaseType: CppBaseType,
        Interface: CppInterface,
        Interface.Method: CppInterface.CppMethod,
        Record: CppRecord,
        Record.Field: CppRecord.CppField,
        Function: CppFunction,
        BaseField: CppBaseField,
        SymbolicConstantField: CppSymbolicConstantField,
        Parameter: CppParameter,
        Constant: CppConstant
    }
    writes_header = True
    writes_source = True
    filters = [quote, headers, needs_optional]

    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.hpp.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/flags.hpp.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.hpp.jinja2", type_def=type_def)
        if type_def.constants:
            self.write_source("source/interface_record.cpp.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.hpp.jinja2", type_def=type_def)
        if type_def.constants:
            self.write_source("source/interface_record.cpp.jinja2", type_def=type_def)

    def generate_function(self, type_def: Function):
        pass
