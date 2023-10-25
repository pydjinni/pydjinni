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
from pydjinni.generator.objc.objcpp.config import ObjcppConfig
from pydjinni.parser.ast import Function
from pydjinni.parser.base_models import BaseType, BaseField


class ObjcppExternalType(BaseModel):
    translator: str
    header: Path


class ObjcppBaseType(BaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: ObjcppConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self): return self.decl.name.convert(IdentifierStyle.Case.pascal)

    @computed_field
    @cached_property
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


class ObjcppFunction(ObjcppBaseType):
    decl: Function = Field(exclude=True, repr=False)

    @cached_property
    def name(self): return self.decl.name.title() if self.decl.anonymous else super().name


class ObjcppBaseField(BaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: ObjcppConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(IdentifierStyle.Case.camel)


class ObjcppSymbolicConstantField(ObjcppBaseField):
    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(IdentifierStyle.Case.pascal)
