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

from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from pydjinni.config.types import IdentifierStyle
from pydjinni.generator.filters import headers, quote
from pydjinni.generator.objc.objcpp import external_types
from pydjinni.generator.objc.objcpp.config import ObjcppConfig
from pydjinni.parser.ast import Function, Interface, Record
from pydjinni.parser.base_models import BaseType, BaseField, BaseCommentModel, TypeReference


def translator(type_ref: TypeReference) -> str:
    output = type_ref.type_def.objcpp.translator
    if type_ref.parameters:
        output = f"{output}<{','.join([translator(parameter_ref) for parameter_ref in type_ref.parameters])}>"
    if type_ref.optional:
        output = f"::pydjinni::translators::objc::Optional<{output}>"
    return output


class ObjcppExternalType(BaseModel):
    translator: str
    header: Path


class ObjcBaseModel(BaseModel):
    decl: BaseCommentModel = Field(exclude=True, repr=False)
    config: ObjcppConfig = Field(exclude=True, repr=False)

    @property
    def attributes(self):
        output = []
        if self.decl.deprecated:
            output.append("DEPRECATED_ATTRIBUTE")
        return output


class ObjcppBaseType(ObjcBaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: ObjcppConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self): return self.decl.name.convert(IdentifierStyle.Case.pascal)

    @computed_field
    @property
    def translator(self) -> str:
        output = f"::{self.name}"
        if self.namespace:
            output = f"::{self.namespace}{output}"
        return output

    @computed_field
    @cached_property
    def header(self) -> Path: return Path(f"{self.name}+Private.{self.config.header_extension}")

    @cached_property
    def source(self) -> Path: return Path(f"{self.name}+Private.{self.config.source_extension}")

    @cached_property
    def namespace(self): return '::'.join(self.config.namespace + [identifier.convert(IdentifierStyle.Case.pascal)
                                                                   for identifier in self.decl.namespace])

    @property
    def header_includes(self) -> set[str]: return {
        quote(self.decl.cpp.header)
    }

    @property
    def header_imports(self) -> set[str]: return {
        quote(self.decl.objc.header)
    }

    @property
    def source_includes(self) -> set[str]:
        return headers(self.decl.dependencies, "objcpp") | {
            "<cassert>", quote(Path("pydjinni/objc/error.h"))
        }

    @property
    def source_imports(self) -> set[str]: return {
        quote(self.header)
    }


class ObjcppFunction(ObjcppBaseType):
    decl: Function = Field(exclude=True, repr=False)

    @property
    def source_includes(self) -> set[str]:
        dependency_headers = super().source_includes
        if any([parameter.type_ref.optional for parameter in self.decl.parameters]) or (self.decl.return_type_ref and self.decl.return_type_ref.optional):
            dependency_headers.add(quote(Path("pydjinni/marshal.h")))
        return dependency_headers

    @cached_property
    def name(self): return self.decl.name.title() if self.decl.anonymous else super().name

    @property
    def return_type_translator(self): return translator(self.decl.return_type_ref)


class ObjcppBaseField(ObjcBaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: ObjcppConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(IdentifierStyle.Case.camel)

    @property
    def translator(self): return translator(self.decl.type_ref)

class ObjcppInterface(ObjcppBaseType):
    decl: Interface = Field(exclude=True, repr=False)

    @cached_property
    def source_includes(self) -> set[str]:
        dependency_headers = super().source_includes
        dependency_headers.update([
            "<memory>",
            quote(Path("pydjinni/cpp_wrapper_cache.h")),
            quote(Path("pydjinni/objc_wrapper_cache.h"))
        ])
        if any(method.asynchronous for method in self.decl.methods):
            dependency_headers.update([
                quote(Path("pydjinni/coroutine/task.hpp")),
                quote(Path("pydjinni/coroutine/schedule.h"))
            ])
            if "objc" in self.decl.targets:
                dependency_headers.add(quote(Path("pydjinni/coroutine/callback_awaitable.hpp")))
        if any(method.deprecated for method in self.decl.methods):
            dependency_headers.add(quote(Path("pydjinni/deprecated.hpp")))
        if any([parameter.type_ref.optional for method in self.decl.methods for parameter in
                method.parameters]) or any(method.return_type_ref.optional for method in self.decl.methods if method.return_type_ref):
            dependency_headers.add(quote(Path("pydjinni/marshal.h")))
        return dependency_headers

    class ObjcppMethod(ObjcppBaseField):
        decl: Interface.Method = Field(exclude=True, repr=False)
        @property
        def return_type_translator(self): return translator(self.decl.return_type_ref)


class ObjcppRecord(ObjcppBaseType):
    decl: Record = Field(exclude=True, repr=False)

    @property
    def header_includes(self) -> set[str]: return {
        quote(self.decl.cpp.derived_header) if self.decl.cpp.base_type else quote(self.decl.cpp.header)
    }

    @property
    def header_imports(self) -> set[str]: return {
        quote(self.decl.objc.derived_header) if self.decl.objc.base_type else quote(self.decl.objc.header)
    }




class ObjcppSymbolicConstantField(ObjcppBaseField):
    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(IdentifierStyle.Case.pascal)

class ObjcppErrorDomain(ObjcppBaseType):
    @property
    def source_includes(self) -> set[str]: return super().source_includes | {
        quote(Path(external_types.external_types["string"].header))
    }
