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
from pydjinni.parser.ast import (
    Interface,
    Record,
    Flags,
    Enum,
    Parameter,
    Function,
    ErrorDomain
)
from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    SymbolicConstantField,
    DataField
)
from .config import ObjcConfig
from .external_types import external_types
from .type import (
    ObjcExternalType,
    ObjcBaseType,
    ObjcBaseField,
    ObjcInterface,
    ObjcSymbolicConstantField,
    ObjcRecord,
    ObjcDataField,
    ObjcParameter,
    ObjcFunction,
    ObjcErrorDomain,
)


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
        Function: ObjcFunction,
        SymbolicConstantField: ObjcSymbolicConstantField,
        Record: ObjcRecord,
        DataField: ObjcDataField,
        Parameter: ObjcParameter,
        ErrorDomain: ObjcErrorDomain,
        ErrorDomain.ErrorCode: ObjcErrorDomain.ObjcErrorCode
    }
    writes_header = True
    writes_source = True
    filters = [quote, headers]
    comment_start_string = None
    comment_end_string = None
    comment_line_prefix = "/// "

    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.jinja2.h", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/flags.jinja2.h", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.jinja2.h", type_def=type_def)
        self.write_source("source/record.jinja2.m", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.jinja2.h", type_def=type_def)

    def generate_function(self, type_def: Function):
        self.write_header("header/function.jinja2.h", type_def=type_def)

    def generate_error_domain(self, type_def: ErrorDomain):
        self.write_header("header/error_domain.jinja2.h", type_def=type_def)
        self.write_source("source/error_domain.jinja2.m", type_def=type_def)

    def generate_bridging_header(self, ast: list[BaseType]):
        if self.config.swift.bridging_header:
            self.write_header(
                template="header/bridging_header.jinja2.h",
                filename=self.config.swift.bridging_header,
                ast=ast
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_bridging_header(ast)
