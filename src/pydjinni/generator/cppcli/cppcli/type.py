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

from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from pydjinni.parser.ast import Record, Interface

from pydjinni.parser.identifier import IdentifierType as Identifier

from pydjinni.parser.ast import Function
from .comment_renderer import XmlCommentRenderer
from .config import CppCliConfig
from .keywords import keywords
from pydjinni.parser.base_models import BaseType, BaseField, TypeReference
from pydjinni.generator.validator import validate


class CppCliExternalType(BaseModel):
    typename: str
    translator: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$"
    )
    header: Path = None
    reference: bool = True


def typename(type_ref: TypeReference) -> str:
    if type_ref:
        output = type_ref.type_def.cppcli.typename
        if type_ref.optional and not type_ref.type_def.cppcli.reference:
            output = f"System::Nullable<{output}>"
        if type_ref.parameters:
            output += f"<{', '.join([typename(type_ref) for type_ref in type_ref.parameters])}>"
        output += "^" if type_ref.type_def.cppcli.reference else ""
        return output
    else:
        return "void"


def translator(type_ref: TypeReference) -> str:
    output = type_ref.type_def.cppcli.translator
    if type_ref.parameters:
        output += f"<{', '.join([translator(type_ref) for type_ref in type_ref.parameters])}>"
    if type_ref.optional:
        output = f"::pydjinni::cppcli::translator::Optional<std::optional, {output}>"
    return output


class CppCliBaseType(BaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: CppCliConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self):
        return self.decl.name.convert(self.config.identifier.type)

    @cached_property
    @validate(keywords, separator="::")
    def namespace(self):
        return '::'.join(self.config.namespace + [identifier.convert(self.config.identifier.namespace) for
                                                  identifier in self.decl.namespace])

    @computed_field
    @cached_property
    def typename(self) -> str:
        return f"::{self.namespace}::{self.name}"

    @computed_field
    @cached_property
    def translator(self) -> str:
        return self.typename

    @cached_property
    def cs_typename(self) -> str:
        return '.'.join(
            self.config.namespace +
            [identifier.convert(self.config.identifier.namespace) for identifier in self.decl.namespace] +
            [self.name]
        )

    @computed_field
    @cached_property
    def header(self) -> Path:
        return Path(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.hpp"

    @cached_property
    def source(self):
        return Path(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.cpp"

    @cached_property
    def comment(self):
        return XmlCommentRenderer(self.config.identifier).render(*self.decl.parsed_comment).strip() \
            if self.decl.comment else ''

    @computed_field
    @cached_property
    def reference(self) -> bool:
        return True


class CppCliBaseField(BaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: CppCliConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self) -> str:
        return self.decl.name.convert(self.config.identifier.local)

    @cached_property
    def typename(self) -> str:
        return typename(self.decl.type_ref)

    @cached_property
    def translator(self) -> str:
        return translator(self.decl.type_ref)

    @cached_property
    def comment(self):
        return XmlCommentRenderer(self.config.identifier).render(*self.decl.parsed_comment).strip() \
            if self.decl.comment else ''


class CppCliMethodField(CppCliBaseField):
    decl: Interface.Method = Field(exclude=True, repr=False)

    @cached_property
    def name(self) -> str:
        return self.decl.name.convert(self.config.identifier.method)

    @cached_property
    def typename(self) -> str:
        return typename(self.decl.return_type_ref)

    @cached_property
    def translator(self) -> str:
        return translator(self.decl.return_type_ref)


class CppCliRecord(CppCliBaseType):

    def base_name(self) -> Identifier:
        name = self.decl.name
        if self.base_type:
            name += "_base"
        return Identifier(name)

    @cached_property
    def base_type(self) -> bool:
        return "cppcli" in self.decl.targets

    @cached_property
    def name(self):
        return self.base_name().convert(self.config.identifier.type)

    @cached_property
    def derived_name(self) -> str:
        return Identifier(self.decl.name).convert(self.config.identifier.type)

    @computed_field
    @cached_property
    def typename(self) -> str:
        name = self.decl.name.convert(self.config.identifier.type)
        return f"::{self.namespace}::{name}"

    @computed_field
    @cached_property
    def header(self) -> Path:
        return Path(
            *self.decl.namespace) / f"{self.base_name().convert(self.config.identifier.file)}.hpp"

    @computed_field
    @cached_property
    def derived_header(self) -> Path:
        return Path(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.hpp"

    @cached_property
    def source(self):
        return Path(
            *self.decl.namespace) / f"{self.base_name().convert(self.config.identifier.file)}.cpp"

    class Field(CppCliBaseField):
        decl: Record.Field = Field(exclude=True, repr=False)

        @cached_property
        def property(self) -> str:
            return self.decl.name.convert(self.config.identifier.property)

        @cached_property
        def equals(self) -> str:
            if self.decl.type_ref.type_def.cppcli.reference:
                return f"{self.property}->Equals(other->{self.property})"
            else:
                return f"{self.property} == other->{self.property}"

        @cached_property
        def compare(self) -> str:
            if self.decl.type_ref.type_def.name == 'string':
                return f"System::String::Compare({self.property}, other->{self.property}, System::StringComparison::Ordinal);"
            else:
                return f"{self.property}.CompareTo(other->{self.property})"


class CppCliSymbolicConstant(CppCliBaseType):

    @computed_field
    @cached_property
    def reference(self) -> bool:
        return False

    @cached_property
    def translator(self) -> str:
        return f"::pydjinni::cppcli::translator::Enum<{self.decl.cpp.typename}, {self.typename}>"

    class Field(CppCliBaseField):
        @computed_field
        @cached_property
        @validate(keywords)
        def name(self) -> str: return self.decl.name.convert(self.config.identifier.enum)


class CppCliFunction(CppCliBaseType):
    decl: Function = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def typename(self) -> str:
        if self.decl.anonymous:
            parameters = ', '.join([param.cppcli.typename for param in self.decl.parameters])
            if self.decl.return_type_ref:
                return f"System::Func<{parameters}, {self.return_typename}>"
            elif self.decl.parameters:
                return f"System::Action<{parameters}>"
            else:
                return "System::Action"
        else:
            return super().typename

    @cached_property
    def delegate_name(self) -> str:
        return f'_{Identifier(self.decl.name + "_delegate").convert(self.config.identifier.type)}'

    @cached_property
    def delegate_typename(self) -> str:
        return f"{self.namespace}::{self.delegate_name}"

    @cached_property
    def return_typename(self) -> str:
        return typename(self.decl.return_type_ref)

    @computed_field
    @cached_property
    def translator(self) -> str:
        return f"{self.namespace}::{self.delegate_name}"

