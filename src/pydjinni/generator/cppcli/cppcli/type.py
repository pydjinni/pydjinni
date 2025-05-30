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
from pathlib import PurePosixPath

from pydantic import BaseModel, Field, computed_field

from pydjinni.parser.ast import Interface, Record

from pydjinni.parser.identifier import IdentifierType as Identifier

from pydjinni.parser.ast import Function
from .comment_renderer import XmlCommentRenderer
from .config import CppCliConfig
from .keywords import keywords
from pydjinni.parser.base_models import BaseType, BaseField, TypeReference, DataField, BaseCommentModel
from pydjinni.generator.validator import validate

from pydjinni.generator.filters import headers, quote


class CppCliExternalType(BaseModel):
    typename: str
    translator: str
    header: PurePosixPath = None
    reference: bool = True


def typename(type_ref: TypeReference, asynchronous: bool = False) -> str:
    if type_ref:
        output = type_ref.type_def.cppcli.typename
        if type_ref.optional and not type_ref.type_def.cppcli.reference:
            output = f"System::Nullable<{output}>"
        if type_ref.parameters:
            output += f"<{', '.join([typename(type_ref) for type_ref in type_ref.parameters])}>"
        output += "^" if type_ref.type_def.cppcli.reference else ""
        return output if not asynchronous else f"System::Threading::Tasks::Task<{output}>^"
    else:
        return "void" if not asynchronous else "System::Threading::Tasks::Task^"


def translator(type_ref: TypeReference) -> str:
    output = type_ref.type_def.cppcli.translator
    if type_ref.parameters:
        output += f"<{', '.join([translator(type_ref) for type_ref in type_ref.parameters])}>"
    if type_ref.optional:
        output = f"::pydjinni::cppcli::translator::Optional<{output}>"
    return output

class CppCliBaseCommentModel(BaseModel):
    decl: BaseCommentModel = Field(exclude=True, repr=False)
    config: CppCliConfig = Field(exclude=True, repr=False)

    @cached_property
    def comment(self):
        return XmlCommentRenderer(self.config.identifier).render(*self.decl._parsed_comment).strip() \
            if self.decl._parsed_comment else ''

    @property
    def deprecated(self):
        message = ""
        if isinstance(self.decl.deprecated, str):
            message = '("' + self.decl.deprecated.replace('\n', r'\n').replace('"', r'\"') + '")'
        return f"[System::Obsolete{message}]"


class CppCliBaseType(CppCliBaseCommentModel):
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
    def header(self) -> PurePosixPath:
        return PurePosixPath(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.hpp"

    @cached_property
    def source(self) -> PurePosixPath:
        return PurePosixPath(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.cpp"


    @computed_field
    @cached_property
    def reference(self) -> bool:
        return True

    @property
    def header_includes(self) -> set[str]: return headers(self.decl.dependencies, "cppcli") | {
        quote(self.decl.cpp.header)
    }

    @property
    def source_includes(self) -> set[str]: return {
        quote(self.header),
        quote(PurePosixPath("pydjinni/cppcli/Assert.hpp")),
        quote(PurePosixPath("pydjinni/cppcli/Marshal.hpp"))
    }


class CppCliBaseField(CppCliBaseCommentModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: CppCliConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self) -> str:
        return self.decl.name.convert(self.config.identifier.local)

    @cached_property
    def property(self) -> str:
        return self.decl.name.convert(self.config.identifier.property)

    @cached_property
    def typename(self) -> str:
        return typename(self.decl.type_ref)

    @cached_property
    def translator(self) -> str:
        return translator(self.decl.type_ref)

    @cached_property
    def nullability_attribute(self) -> str:
        if self.config.nullability_attributes and self.decl.type_ref:
            return f"[{'System::Diagnostics::CodeAnalysis::AllowNull' if self.decl.type_ref.optional else 'System::Diagnostics::CodeAnalysis::DisallowNull'}] "
        else:
            return ""


class CppCliInterface(CppCliBaseType):

    @property
    def header_includes(self) -> set[str]:
        dependency_headers = super().header_includes
        if any(method.asynchronous for method in self.decl.methods):
            dependency_headers.update([
                quote(PurePosixPath("pydjinni/coroutine/task.hpp")),
                quote(PurePosixPath("pydjinni/coroutine/schedule.hpp"))
            ])
            if "cppcli" in self.decl.targets:
                dependency_headers.add(quote(PurePosixPath("pydjinni/coroutine/callback_awaitable.hpp")))
        return dependency_headers

    @property
    def source_includes(self) -> set[str]: return super().source_includes | {
        quote(PurePosixPath("pydjinni/cppcli/Error.hpp")),
        quote(PurePosixPath("pydjinni/cppcli/WrapperCache.hpp"))
    }

    class CppCliMethod(CppCliBaseField):
        decl: Interface.Method = Field(exclude=True, repr=False)

        @cached_property
        def name(self) -> str:
            return self.decl.name.convert(self.config.identifier.method)

        @cached_property
        def typename(self) -> str:
            return typename(self.decl.return_type_ref, self.decl.asynchronous)

        @cached_property
        def synchronous_typename(self) -> str:
            return typename(self.decl.return_type_ref)

        @cached_property
        def translator(self) -> str:
            return translator(self.decl.return_type_ref)

        @cached_property
        def async_proxy_name(self) -> str:
            return Identifier(self.decl.name + "_proxy").convert(self.config.identifier.method)

        @cached_property
        def nullability_attribute(self) -> str:
            if self.config.nullability_attributes and self.decl.return_type_ref:
                return f"[returnvalue: {'System::Diagnostics::CodeAnalysis::MaybeNull' if self.decl.return_type_ref.optional and not self.decl.return_type_ref.asynchronous else 'System::Diagnostics::CodeAnalysis::NotNull'}]"
            else:
                return ""

class CppCliRecord(CppCliBaseType):
    decl: Record = Field(exclude=True, repr=False)

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
    def header(self) -> PurePosixPath:
        return PurePosixPath(
            *self.decl.namespace) / f"{self.base_name().convert(self.config.identifier.file)}.hpp"

    @computed_field
    @cached_property
    def derived_header(self) -> PurePosixPath:
        return PurePosixPath(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.hpp"

    @cached_property
    def source(self) -> PurePosixPath:
        return PurePosixPath(
            *self.decl.namespace) / f"{self.base_name().convert(self.config.identifier.file)}.cpp"

    @property
    def header_includes(self) -> set[str]: return headers(self.decl.dependencies, "cppcli") | {
            quote(self.decl.cpp.derived_header) if self.decl.cpp.base_type else quote(self.decl.cpp.header)
        }

    @property
    def source_includes(self) -> set[str]: return {
        quote(PurePosixPath("pydjinni/cppcli/Assert.hpp")),
        quote(PurePosixPath("pydjinni/cppcli/Marshal.hpp")),
        quote(self.derived_header) if self.base_type else quote(self.header)
    }

class CppCliDataField(CppCliBaseField):
    decl: DataField = Field(exclude=True, repr=False)

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


    @cached_property
    def property_nullability_attribute(self) -> str:
        if self.config.nullability_attributes and self.decl.type_ref:
            return f"[{'System::Diagnostics::CodeAnalysis::MaybeNull' if self.decl.type_ref.optional else 'System::Diagnostics::CodeAnalysis::NotNull'}]"
        else:
            return ""

    @cached_property
    def constructor_nullability_attribute(self) -> str:
        if self.config.nullability_attributes and self.decl.type_ref:
            return f"[{'System::Diagnostics::CodeAnalysis::AllowNull' if self.decl.type_ref.optional else 'System::Diagnostics::CodeAnalysis::DisallowNull'}] "
        else:
            return ""


class CppCliSymbolicConstant(CppCliBaseType):

    @computed_field
    @cached_property
    def reference(self) -> bool:
        return False

    @cached_property
    def translator(self) -> str:
        return f"::pydjinni::cppcli::translator::Enum<{self.decl.cpp.typename},{self.typename}>"

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

    @property
    def header_includes(self) -> set[str]:
        return super().header_includes | { "<functional>", "<vcclr.h>" }

    @property
    def source_includes(self) -> set[str]: return super().source_includes | {
        quote(PurePosixPath("pydjinni/cppcli/Error.hpp"))
    }


class CppCliErrorDomain(CppCliBaseType):
    pass

    class CppCliErrorCode(CppCliBaseField):
        @cached_property
        def name(self) -> str:
            return self.decl.name.convert(self.config.identifier.type)
