# Copyright 2023 - 2024 jothepro
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
    SymbolicConstantField
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
    CppParameter
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
        Parameter: CppParameter
    }
    writes_header = True
    writes_source = True
    filters = [quote, headers, needs_optional]

    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.hpp.jinja2", type_def=type_def)
        if self.config.string_serialization_for_enums:
            self.write_source("source/enum.cpp.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/flags.hpp.jinja2", type_def=type_def)
        if self.config.string_serialization_for_enums:
            self.write_source("source/flags.cpp.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.hpp.jinja2", type_def=type_def)
        if (Record.Deriving.eq in type_def.deriving
                or Record.Deriving.ord in type_def.deriving
                or Record.Deriving.str in type_def.deriving
                and type_def.fields):
            self.write_source("source/record.cpp.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.hpp.jinja2", type_def=type_def)

    def generate_function(self, type_def: Function):
        pass
