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

from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Enum, Flags, Record, Interface, Function
from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    SymbolicConstantField
)
from .config import JavaConfig
from .external_types import external_types
from .type import (
    JavaExternalType,
    JavaBaseType,
    JavaRecord,
    JavaFlags,
    JavaFunction,
    JavaBaseField,
    JavaSymbolicConstantField,
    JavaInterface
)


class JavaGenerator(Generator):
    key = "java"
    config_model = JavaConfig
    external_type_model = JavaExternalType
    external_types = external_types
    marshal_models = {
        BaseType: JavaBaseType,
        Record: JavaRecord,
        Record.Field: JavaRecord.JavaField,
        Flags: JavaFlags,
        Function: JavaFunction,
        BaseField: JavaBaseField,
        SymbolicConstantField: JavaSymbolicConstantField,
        Interface: JavaInterface,
        Interface.Method: JavaInterface.JavaMethod
    }
    writes_source = True

    def generate_enum(self, type_def: Enum):
        self.write_source("enum.java.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_source("flags.java.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_source("record.java.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_source("interface.java.jinja2", type_def=type_def)

    def generate_function(self, type_def: Function):
        self.write_source("function.java.jinja2", type_def=type_def)

    def generate_loader(self):
        if self.config.native_lib:
            loader = f"{self.config.native_lib}Loader"
            package = '.'.join(self.config.package + ["native_lib"])
            package_path = Path("/".join(package.split(".")))
            self.write_source(
                template="loader.java.jinja2",
                filename=package_path / f"{loader}.java",
                loader=loader,
                package=package
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_loader()
