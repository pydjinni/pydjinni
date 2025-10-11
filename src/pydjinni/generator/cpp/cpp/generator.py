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
from pathlib import Path

from pydjinni.generator.filters import headers, quote
from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum, Function, Parameter, ErrorDomain
from pydjinni.parser.base_models import BaseType, BaseField, DataField, SymbolicConstantField, SymbolicConstantType
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
    CppParameter,
    CppDataField,
    CppErrorDomain,
    CppEnum,
    CppFlags,
    CppSymbolicConstantType,
)


class CppGenerator(Generator[CppConfig, CppExternalType]):
    key = "cpp"
    external_types = external_types
    marshal_models = {
        BaseType: CppBaseType,
        Interface: CppInterface,
        Interface.Method: CppInterface.CppMethod,
        Interface.Property: CppInterface.CppProperty,
        Record: CppRecord,
        DataField: CppDataField,
        Function: CppFunction,
        BaseField: CppBaseField,
        Enum: CppEnum,
        Flags: CppFlags,
        SymbolicConstantField: CppSymbolicConstantType.CppSymbolicConstantField,
        Parameter: CppParameter,
        ErrorDomain: CppErrorDomain,
        ErrorDomain.ErrorCode: CppErrorDomain.CppErrorCode,
    }
    writes_header = True
    writes_source = True
    filters = [quote, headers, needs_optional]

    def generate_enum(self, type_def: Enum):
        self.write_header(Path("header/enum.jinja2.hpp"), type_def)
        if self.config.string_serialization:
            self.write_source(Path("source/enum.jinja2.cpp"), type_def)

    def generate_error_domain(self, type_def: ErrorDomain):
        self.write_header(Path("header/error_domain.jinja2.hpp"), type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header(Path("header/flags.jinja2.hpp"), type_def)
        if self.config.string_serialization:
            self.write_source(Path("source/flags.jinja2.cpp"), type_def)

    def generate_record(self, type_def: Record):
        self.write_header(Path("header/record.jinja2.hpp"), type_def)
        has_cpp_base_type = not type_def.cpp.base_type  # type: ignore[attr-defined]
        if (
            Record.Deriving.eq in type_def.deriving
            or Record.Deriving.ord in type_def.deriving
            or (self.config.string_serialization and has_cpp_base_type)
            and type_def.fields
        ):
            self.write_source(Path("source/record.jinja2.cpp"), type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header(Path("header/interface.jinja2.hpp"), type_def)
        if type_def.properties:
            self.write_source(Path("source/interface.jinja2.cpp"), type_def)

    def generate_function(self, type_def: Function):
        self.write_header(Path("header/function.jinja2.hpp"), type_def)
