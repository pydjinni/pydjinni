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

from pathlib import Path

from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import (
    Enum,
    Flags,
    Record,
    Interface,
    Function,
    ErrorDomain, Parameter
)
from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    SymbolicConstantField,
    DataField
)
from .config import JavaConfig
from .external_types import external_types
from .metadata import JavaMetadata
from .type import (
    JavaExternalType,
    JavaBaseType,
    JavaRecord,
    JavaFlags,
    JavaFunction,
    JavaBaseField,
    JavaSymbolicConstantField,
    JavaInterface,
    JavaErrorDomain,
    JavaDataField,
    NativeLibLoader,
    NativeCleaner
)


class JavaGenerator(Generator):
    key = "java"
    config_model = JavaConfig
    external_type_model = JavaExternalType
    external_types = external_types
    marshal_models = {
        BaseType: JavaBaseType,
        Record: JavaRecord,
        DataField: JavaDataField,
        Parameter: JavaDataField,
        Flags: JavaFlags,
        Function: JavaFunction,
        BaseField: JavaBaseField,
        SymbolicConstantField: JavaSymbolicConstantField,
        Interface: JavaInterface,
        Interface.Method: JavaInterface.JavaMethod,
        ErrorDomain: JavaErrorDomain,
        ErrorDomain.ErrorCode: JavaErrorDomain.JavaErrorCode,
    }
    metadata_model = JavaMetadata
    writes_source = True

    def generate_enum(self, type_def: Enum):
        self.write_source("enum.jinja2.java", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_source("flags.jinja2.java", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_source("record.jinja2.java", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_source(
            template="interface.jinja2.java",
            type_def=type_def,
            native_lib_loader=NativeLibLoader(self.config),
            native_cleaner=NativeCleaner(self.config)
        )

    def generate_function(self, type_def: Function):
        self.write_source(
            template="function.jinja2.java",
            type_def=type_def,
            native_cleaner=NativeCleaner(self.config)
        )

    def generate_error_domain(self, type_def: ErrorDomain):
        self.write_source(
            template="error_domain.jinja2.java",
            type_def=type_def
        )

    def generate_loader(self):
        native_lib_loader = NativeLibLoader(self.config)
        self.write_source(
            template="loader.jinja2.java",
            filename=native_lib_loader.source,
            native_lib_loader=native_lib_loader
        )

    def generate_runnable(self):
        package = '.'.join(self.config.package + self.config.support_types_package)
        package_path = Path("/".join(package.split(".")))
        self.write_source(
            template="runnable.jinja2.java",
            filename=package_path / f"NativeRunnable.java",
            package=package,
            native_cleaner=NativeCleaner(self.config)
        )

    def generate_completion(self):
        package = '.'.join(self.config.package + self.config.support_types_package)
        package_path = Path("/".join(package.split(".")))
        self.write_source(
            template="completion.jinja2.java",
            filename=package_path / f"NativeCompletion.java",
            package=package,
            native_cleaner=NativeCleaner(self.config)
        )

    def generate_cleaner(self):
        native_cleaner = NativeCleaner(self.config)
        self.write_source(
            template="cleaner.jinja2.java",
            filename=native_cleaner.source,
            native_cleaner=native_cleaner
        )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_cleaner()
        if self.config.native_lib:
            self.generate_loader()
        if any(
            isinstance(type_def, Interface) and "cpp" in type_def.targets and any(method.asynchronous for method in type_def.methods)
            for type_def in ast
        ):
            self.generate_runnable()
        if any(
            isinstance(type_def, Interface) and "java" in type_def.targets and any(method.asynchronous for method in type_def.methods)
            for type_def in ast
        ):
            self.generate_completion()
