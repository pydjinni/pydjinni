# Copyright 2023 jothepro
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

from pydjinni.generator.filters import quote, headers
from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Enum, Flags, Record, Interface, Parameter, Function
from pydjinni.parser.base_models import BaseType, BaseField, SymbolicConstantField
from .config import JniConfig
from .external_types import external_types
from .type import (
    JniExternalType,
    JniBaseType,
    JniInterface,
    JniBaseField,
    JniSymbolicConstantField,
    JniRecord,
    JniParameter,
    JniFunction
)


class JniGenerator(Generator):
    key = "jni"
    config_model = JniConfig
    external_type_model = JniExternalType
    external_types = external_types
    marshal_models = {
        BaseType: JniBaseType,
        Interface: JniInterface,
        Interface.Method: JniInterface.JniMethod,
        Function: JniFunction,
        BaseField: JniBaseField,
        SymbolicConstantField: JniSymbolicConstantField,
        Record: JniRecord,
        Record.Field: JniRecord.JniField,
        Parameter: JniParameter
    }
    writes_header = True
    writes_source = True
    support_lib_commons = True
    filters = [quote, headers]

    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.hpp.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/flags.hpp.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.hpp.jinja2", type_def=type_def)
        self.write_source("source/record.cpp.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.hpp.jinja2", type_def=type_def)
        self.write_source("source/interface.cpp.jinja2", type_def=type_def)

    def generate_function(self, type_def: Function):
        self.write_header("header/function.hpp.jinja2", type_def=type_def)
        self.write_source("source/function.cpp.jinja2", type_def=type_def)

    def generate_loader(self):
        if self.config.loader:
            self.write_source(
                template="source/loader.cpp.jinja2",
                filename=Path("pydjinni") / "jni" / "loader.cpp"
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_loader()
