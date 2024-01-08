# Copyright 2024 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import (
    Interface,
    Record,
    Flags,
    Enum,
    Function
)
from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    SymbolicConstantField, SymbolicConstantType
)
from .config import CppCliConfig
from .external_types import external_types
from .type import (
    CppCliExternalType,
    CppCliBaseType,
    CppCliBaseField,
    CppCliRecord,
    CppCliMethodField,
    CppCliSymbolicConstant, CppCliFunction
)
from pydjinni.generator.filters import quote, headers


class CppCliGenerator(Generator):
    key = "cppcli"
    config_model = CppCliConfig
    external_type_model = CppCliExternalType
    external_types = external_types
    marshal_models = {
        BaseType: CppCliBaseType,
        BaseField: CppCliBaseField,
        Record: CppCliRecord,
        Record.Field: CppCliRecord.Field,
        Interface.Method: CppCliMethodField,
        SymbolicConstantField: CppCliSymbolicConstant.Field,
        SymbolicConstantType: CppCliSymbolicConstant,
        Function: CppCliFunction
    }
    filters = [quote, headers]
    support_lib_commons = True
    writes_header = True
    writes_source = True

    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.hpp.jinja2", type_def=type_def)
        self.write_source("source/placeholder.cpp.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/flags.hpp.jinja2", type_def=type_def)
        self.write_source("source/placeholder.cpp.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.hpp.jinja2", type_def=type_def)
        self.write_source("source/record.cpp.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.hpp.jinja2", type_def=type_def)
        self.write_source("source/interface.cpp.jinja2", type_def=type_def)

    def generate_function(self, type_def: Function):
        self.write_header("header/function.hpp.jinja2", type_def=type_def)
        self.write_source("source/function.cpp.jinja2", type_def=type_def)
