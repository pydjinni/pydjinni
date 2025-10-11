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
from pydjinni.generator.java.java.metadata import JavaMetadata
from pydjinni.parser.ast import Enum, Flags, Record, Interface, Parameter, Function, ErrorDomain
from pydjinni.parser.base_models import BaseType, BaseField, SymbolicConstantField, DataField
from .config import JniConfig
from .external_types import external_types
from .type import (
    JniExternalType,
    JniBaseType,
    JniInterface,
    JniBaseField,
    JniSymbolicConstantField,
    JniRecord,
    JniDataField,
    JniParameter,
    JniFunction,
    JniErrorDomain,
    jni_prefix,
)


class JniGenerator(Generator[JniConfig, JniExternalType]):
    key = "jni"
    external_types = external_types
    marshal_models = {
        BaseType: JniBaseType,
        Interface: JniInterface,
        Interface.Method: JniInterface.JniMethod,
        Interface.Property: JniInterface.JniProperty,
        Function: JniFunction,
        BaseField: JniBaseField,
        SymbolicConstantField: JniSymbolicConstantField,
        Record: JniRecord,
        DataField: JniDataField,
        Parameter: JniParameter,
        ErrorDomain: JniErrorDomain,
    }
    writes_header = True
    writes_source = True
    support_lib_commons = True
    filters = [quote, headers]

    def generate_enum(self, type_def: Enum):
        self.write_header(Path("header/enum.jinja2.hpp"), type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header(Path("header/flags.jinja2.hpp"), type_def)

    def generate_record(self, type_def: Record):
        self.write_header(Path("header/record.jinja2.hpp"), type_def)
        self.write_source(Path("source/record.jinja2.cpp"), type_def)

    def generate_interface(self, type_def: Interface):
        java_metadata: JavaMetadata = self.metadata.java # type: ignore
        callback_type = java_metadata.support_types_package.split(".") + ["OnPropertyChangedCallback"]
        connection_type = java_metadata.support_types_package.split(".") + ["Connection"]
        self.write_header(
            Path("header/interface.jinja2.hpp"),
            type_def=type_def,
            callback_type="/".join(callback_type),
            connection_type="/".join(connection_type),
        )
        self.write_source(Path("source/interface.jinja2.cpp"), type_def, callback_type="/".join(callback_type))

    def generate_function(self, type_def: Function):
        self.write_header(Path("header/function.jinja2.hpp"), type_def)
        self.write_source(Path("source/function.jinja2.cpp"), type_def)

    def generate_error_domain(self, type_def: ErrorDomain):
        self.write_header(Path("header/error_domain.jinja2.hpp"), type_def)
        self.write_source(Path("source/error_domain.jinja2.cpp"), type_def)

    def generate_loader(self):
        self.write_source(template=Path("source/loader.jinja2.cpp"), filename=self.source_path / "loader.cpp")

    def generate_runnable(self):
        header_path = Path("pydjinni") / "coroutine" / "schedule.hpp"
        java_runnable_type = self.metadata.java.support_types_package.split(".") + ["NativeRunnable"]
        self.write_header(
            template=Path("header/schedule.jinja2.hpp"),
            filename=self.header_path / header_path,
            java_type_signature="/".join(java_runnable_type),
            namespace="::".join(self.config.namespace + ["schedule"]),
        )
        self.write_source(
            template=Path("source/schedule.jinja2.cpp"),
            filename=self.source_path / "pydjinni" / "coroutine" / "schedule.cpp",
            namespace="::".join(self.config.namespace + ["schedule"]),
            header_path=header_path,
            jni_prefix=jni_prefix(java_runnable_type),
        )

    def generate_completion(self):
        header_path = Path("pydjinni") / "coroutine" / "completion.hpp"
        java_runnable_type = self.metadata.java.support_types_package.split(".") + ["NativeCompletion"]
        self.write_header(
            template=Path("header/completion.jinja2.hpp"),
            filename=self.header_path / header_path,
            java_type_signature="/".join(java_runnable_type),
            namespace="::".join(self.config.namespace + ["schedule"]),
        )
        self.write_source(
            template=Path("source/completion.jinja2.cpp"),
            filename=self.source_path / "pydjinni" / "coroutine" / "completion.cpp",
            namespace="::".join(self.config.namespace + ["schedule"]),
            header_path=header_path,
            jni_prefix=jni_prefix(java_runnable_type),
        )

    def generate_property_support_types(self):
        header_path = Path("pydjinni") / "jni" / "connection.hpp"
        on_property_changed_header_path = Path("pydjinni") / "jni" / "on_property_changed_callback.hpp"
        java_runnable_type = self.metadata.java.support_types_package.split(".") + ["Connection$CppProxy"]
        java_on_property_changed_callback_type = self.metadata.java.support_types_package.split(".") + [
            "OnPropertyChangedCallback$CppProxy"
        ]
        self.write_header(
            template=Path("header/connection.jinja2.hpp"),
            filename=self.header_path / header_path,
            java_type_signature="/".join(java_runnable_type),
            namespace="::".join(self.config.namespace + ["signal"]),
        )
        self.write_source(
            template=Path("source/connection.jinja2.cpp"),
            filename=self.source_path / "pydjinni" / "signal" / "connection.cpp",
            namespace="::".join(self.config.namespace + ["signal"]),
            header_path=header_path,
            jni_prefix=jni_prefix(java_runnable_type),
        )
        self.write_header(
            template=Path("header/on_property_changed_callback.jinja2.hpp"),
            filename=self.header_path / on_property_changed_header_path,
            java_type_signature="/".join(java_on_property_changed_callback_type),
            namespace="::".join(self.config.namespace),
        )
        self.write_source(
            template=Path("source/on_property_changed_callback.jinja2.cpp"),
            filename=self.source_path / "pydjinni" / "signal" / "on_property_changed_callback.cpp",
            namespace="::".join(self.config.namespace),
            header_path=on_property_changed_header_path,
            jni_prefix=jni_prefix(java_on_property_changed_callback_type),
        )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        if self.config.loader:
            self.generate_loader()
        if any(
            isinstance(type_def, Interface)
            and "cpp" in type_def.targets
            and any(method.asynchronous for method in type_def.methods)
            for type_def in ast
        ):
            self.generate_runnable()
        if any(
            isinstance(type_def, Interface)
            and "java" in type_def.targets
            and any(method.asynchronous for method in type_def.methods)
            for type_def in ast
        ):
            self.generate_completion()
        if any(
            isinstance(type_def, Interface) and "cpp" in type_def.targets and type_def.properties for type_def in ast
        ):
            self.generate_property_support_types()
