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

from pydjinni.generator.filters import quote, headers
from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum, Function
from pydjinni.parser.base_models import BaseType, BaseField, SymbolicConstantField
from .config import ObjcppConfig
from .external_types import external_types
from .type import ObjcppExternalType, ObjcppBaseType, ObjcppBaseField, ObjcppSymbolicConstantField, ObjcppFunction


class ObjcppGenerator(Generator):
    key = "objcpp"
    config_model = ObjcppConfig
    external_type_model = ObjcppExternalType
    external_types = external_types
    marshal_models = {
        BaseType: ObjcppBaseType,
        BaseField: ObjcppBaseField,
        Function: ObjcppFunction,
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

    def generate_function(self, type_def: Function):
        self.write_header("header/function.h.jinja2", type_def=type_def)
        self.write_source("source/function.mm.jinja2", type_def=type_def)
