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

from pydjinni.generator.cpp.cpp.comment_renderer import DoxygenCommentRenderer
from pydjinni.generator.cpp.cpp.config import CppConfig
from pydjinni.generator.cpp.cpp.keywords import keywords
from pydjinni.generator.validator import validate
from pydjinni.parser.ast import Parameter, Record, Interface
from pydjinni.parser.base_models import BaseType, BaseField, TypeReference, BaseExternalType
from pydjinni.parser.identifier import IdentifierType as Identifier


class CppExternalType(BaseModel):
    typename: str = Field(
        description="Must be a valid C++ type identifier",
        examples=[
            "int8_t", "::some::Type"
        ]
    )
    header: Path = None
    by_value: bool = False


def type_specifier(type_ref: TypeReference, is_parameter: bool = False):
    output = type_ref.type_def.cpp.typename if type_ref else "void"
    if type_ref:
        if type_ref.parameters:
            parameter_output = ""
            for parameter in type_ref.parameters:
                if parameter_output:
                    parameter_output += ", "
                parameter_output += type_specifier(parameter)
            output += f"<{parameter_output}>"
        if (isinstance(type_ref.type_def,
                       BaseExternalType) and type_ref.type_def.primitive == BaseExternalType.Primitive.interface) or \
                isinstance(type_ref.type_def, Interface):
            output = f"std::shared_ptr<{output}>"
        elif type_ref.optional:
            output = f"std::optional<{output}>"
    return f"const {output} &" if is_parameter and not type_ref.type_def.cpp.by_value else output


class CppBaseType(BaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: CppConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self): return self.decl.name.convert(self.config.identifier.type)

    @cached_property
    @validate(keywords, separator="::")
    def namespace(self): return '::'.join(
        self.config.namespace + [identifier.convert(self.config.identifier.namespace) for
                                 identifier in self.decl.namespace])

    @computed_field
    @cached_property
    def typename(self) -> str:
        output = f"::{self.name}"
        if self.namespace:
            output = f"::{self.namespace}{output}"
        return output

    @computed_field
    @cached_property
    def header(self) -> Path:
        return Path(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.{self.config.header_extension}"

    @cached_property
    def source(self): return Path(
        *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.{self.config.source_extension}"

    @cached_property
    def comment(self):
        return DoxygenCommentRenderer(self.config.identifier).render_tokens(*self.decl.parsed_comment).strip() \
            if self.decl.comment else ''

    @computed_field
    @cached_property
    def by_value(self) -> bool: return True

    @cached_property
    def proxy(self): return False


class CppBaseField(BaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: CppConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    @validate(keywords)
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.field)

    @cached_property
    def comment(self):
        return DoxygenCommentRenderer(self.config.identifier).render_tokens(*self.decl.parsed_comment).strip() \
            if self.decl.comment else ''


class CppInterface(CppBaseType):
    @cached_property
    def proxy(self): return "cpp" in self.decl.targets

    @computed_field
    @cached_property
    def by_value(self) -> bool: return False

    class CppMethod(CppBaseField):
        decl: Interface.Method = Field(exclude=True, repr=False)

        @computed_field
        @cached_property
        @validate(keywords)
        def name(self) -> str: return self.decl.name.convert(self.config.identifier.method)

        @cached_property
        def type_spec(self): return type_specifier(self.decl.return_type_ref)

        @cached_property
        def attribute(self): return "static" if self.decl.static else "virtual"


class CppRecord(CppBaseType):
    decl: Record = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def by_value(self) -> bool:
        return False

    @cached_property
    def base_type(self) -> bool:
        return "cpp" in self.decl.targets

    @cached_property
    def derived_name(self) -> str:
        return Identifier(self.decl.name).convert(self.config.identifier.type)

    @cached_property
    def name(self):
        if self.base_type:
            return Identifier(f"{self.decl.name}_base").convert(self.config.identifier.type)
        else:
            return super().name

    @computed_field
    @cached_property
    def typename(self) -> str:
        output = f"::{self.derived_name}"
        if self.namespace:
            output = f"::{self.namespace}{output}"
        return output

    @computed_field
    @cached_property
    def header(self) -> Path:
        if self.base_type:
            filename = Identifier(self.decl.name + "_base").convert(self.config.identifier.file)
            return Path(*self.decl.namespace) / f"{filename}.{self.config.header_extension}"
        else:
            return super().header

    @computed_field
    @cached_property
    def source(self) -> Path:
        if self.base_type:
            filename = Identifier(self.decl.name + "_base").convert(self.config.identifier.file)
            return Path(*self.decl.namespace) / f"{filename}.{self.config.source_extension}"
        else:
            return super().source

    @cached_property
    def derived_header(self) -> Path:
        return Path(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.{self.config.header_extension}"

    class CppField(CppBaseField):
        decl: Record.Field = Field(exclude=True, repr=False)

        @cached_property
        def type_spec(self): return type_specifier(self.decl.type_ref)


class CppFunction(CppBaseType):
    @computed_field
    @cached_property
    def typename(self) -> str: return f"std::function<{type_specifier(self.decl.return_type_ref)}" \
                                      f"({','.join([type_specifier(parameter.type_ref) for parameter in self.decl.parameters])})>"

    @computed_field
    @cached_property
    def header(self) -> Path: return Path("<functional>")

    @computed_field
    @cached_property
    def by_value(self) -> bool: return False

    @cached_property
    def proxy(self): return "cpp" in self.decl.targets

    @cached_property
    def type_spec(self): return type_specifier(self.decl.return_type_ref)


class CppSymbolicConstantField(CppBaseField):
    @computed_field
    @cached_property
    @validate(keywords)
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.enum)


class CppParameter(CppBaseField):
    decl: Parameter = Field(exclude=True, repr=False)

    @cached_property
    def type_spec(self): return type_specifier(self.decl.type_ref, is_parameter=True)
