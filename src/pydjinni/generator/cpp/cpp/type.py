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
from pydjinni.generator.filters import headers, quote
from pydjinni.generator.validator import validate
from pydjinni.parser.ast import Parameter, Record, Interface, Function, Enum, ErrorDomain, Flags
from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    TypeReference,
    BaseExternalType,
    DataField,
    SymbolicConstantType,
    BaseCommentModel
)
from pydjinni.parser.identifier import IdentifierType as Identifier


def append_if(lst: list, item, condition) -> list:
    return lst + ([item] if condition else [])


class CppExternalType(BaseModel):
    typename: str = Field(
        description="Must be a valid C++ type identifier",
        examples=[
            "int8_t", "::some::Type"
        ]
    )
    header: Path = None
    by_value: bool = False


def deprecated(decl: BaseCommentModel, prefix: str = "", postfix: str = ""):
    message = ""
    if isinstance(decl.deprecated, str):
        message = '("' + decl.deprecated.replace('\n', r'\n').replace('"', r'\"') + '")'
    return f"{prefix}[[deprecated{message}]]{postfix}" if decl.deprecated else ""


class CppBaseCommentModel(BaseModel):
    decl: BaseCommentModel = Field(exclude=True, repr=False)
    config: CppConfig = Field(exclude=True, repr=False)

    def _type_specifier(self, type_ref: TypeReference, is_parameter: bool = False, use_notnull: bool = False) -> str:
        output = type_ref.type_def.cpp.typename if type_ref else "void"
        if type_ref:
            if type_ref.parameters:
                parameter_output = ""
                for parameter in type_ref.parameters:
                    if parameter_output:
                        parameter_output += ", "
                    parameter_output += self._type_specifier(parameter)
                output += f"<{parameter_output}>"
            if type_ref.type_def.primitive == BaseExternalType.Primitive.interface:
                output = f"std::shared_ptr<{output}>"
                if use_notnull and self.config.not_null.type and not type_ref.optional:
                    output = f"{self.config.not_null.type}<{output}>"
            elif type_ref.type_def.primitive == BaseExternalType.Primitive.function:
                if use_notnull and self.config.not_null.type and not type_ref.optional:
                    output = f"{self.config.not_null.type}<{output}>"
            elif type_ref.optional:
                output = f"std::optional<{output}>"
        return f"const {output} &" if is_parameter and not type_ref.type_def.cpp.by_value else output

    @cached_property
    def comment(self):
        return DoxygenCommentRenderer(self.config.identifier).render_tokens(*self.decl.parsed_comment).strip()

    @property
    def deprecated(self):
        return deprecated(self.decl, postfix=" ")


class CppBaseType(CppBaseCommentModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: CppConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self):
        return self.decl.name.convert(self.config.identifier.type)

    @cached_property
    @validate(keywords, separator="::")
    def namespace(self):
        return '::'.join(
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
    def source(self):
        return Path(
            *self.decl.namespace) / f"{self.decl.name.convert(self.config.identifier.file)}.{self.config.source_extension}"

    @computed_field
    @cached_property
    def by_value(self) -> bool:
        return True

    @property
    def proxy(self):
        return False

    @property
    def header_includes(self) -> set[str]:
        dependency_headers = headers(self.decl.dependencies, 'cpp')
        if any(dependency.optional for dependency in self.decl.dependencies):
            dependency_headers.add("<optional>")
        if self.config.not_null.header and any(
                not dependency.optional and dependency.type_def.primitive == BaseExternalType.Primitive.interface for
                dependency in self.decl.dependencies):
            dependency_headers.add(self.config.not_null.header)
        return dependency_headers

    @property
    def source_includes(self) -> set[str]:
        return {
            quote(self.header)
        }


class CppBaseField(CppBaseCommentModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: CppConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    @validate(keywords)
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.field)

    @property
    def deprecated(self): return deprecated(self.decl, prefix=" ")


class CppInterface(CppBaseType):
    decl: Interface = Field(exclude=True, repr=False)

    @cached_property
    def proxy(self):
        return "cpp" in self.decl.targets

    @computed_field
    @cached_property
    def by_value(self) -> bool:
        return False

    @cached_property
    def header_includes(self) -> set[str]:
        dependency_headers = super().header_includes | {"<memory>"}
        if any(method.asynchronous for method in self.decl.methods):
            dependency_headers.add(quote(Path("pydjinni/coroutine/task.hpp")))
        return dependency_headers

    class CppMethod(CppBaseField):
        decl: Interface.Method = Field(exclude=True, repr=False)

        @computed_field
        @cached_property
        @validate(keywords)
        def name(self) -> str:
            return self.decl.name.convert(self.config.identifier.method)

        @cached_property
        def type_spec(self):
            if not self.decl.asynchronous:
                return self._type_specifier(self.decl.return_type_ref, use_notnull=True)
            else:
                return f"pydjinni::coroutine::task<{self._type_specifier(self.decl.return_type_ref)}>"

        # used for coroutine callback parameters
        @cached_property
        def callback_type_spec(self):
            return self._type_specifier(self.decl.return_type_ref, is_parameter=True)

        def prefix_specifiers(self, implementation: bool = False) -> str:
            specifiers = ""
            if self.decl.return_type_ref is not None and self.decl.const:
                specifiers += "[[nodiscard]] "
            if self.decl.static:
                specifiers += "static "
            elif not implementation:
                specifiers += "virtual "
            return specifiers

        def postfix_specifiers(self, implementation: bool = False) -> str:
            specifiers = ""
            if self.decl.const:
                specifiers += " const"
            if self.noexcept:
                specifiers += " noexcept"
            if not self.decl.static and not implementation:
                specifiers += " = 0"
            return specifiers

        @property
        def deprecated(self):
            return deprecated(self.decl, postfix=" ")

        @property
        def noexcept(self) -> bool:
            return self.decl.throwing is None


class CppSymbolicConstantType(CppBaseType):
    decl: SymbolicConstantType = Field(exclude=True, repr=False)

    @property
    def header_includes(self) -> set[str]:
        output = super().header_includes
        if self.config.string_serialization:
            output.add("<format>")
        if self.decl.deprecated:
            output.add(quote(Path("pydjinni/deprecated.hpp")))
        return output

    class CppSymbolicConstantField(CppBaseField):
        @computed_field
        @cached_property
        @validate(keywords)
        def name(self) -> str: return self.decl.name.convert(self.config.identifier.enum)


class CppEnum(CppSymbolicConstantType):
    decl: Enum = Field(exclude=True, repr=False)

    @property
    def source_includes(self) -> set[str]:
        output = super().source_includes
        if any(item.deprecated for item in self.decl.items):
            output.add(quote(Path("pydjinni/deprecated.hpp")))
        return output


class CppFlags(CppSymbolicConstantType):
    decl: Flags = Field(exclude=True, repr=False)

    @property
    def source_includes(self) -> set[str]:
        output = super().source_includes
        if any(flag.deprecated for flag in self.decl.flags):
            output.add(quote(Path("pydjinni/deprecated.hpp")))
        return output


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

    @property
    def header_includes(self) -> set[str]:
        includes = super().header_includes | {"<algorithm>"}
        if self.config.string_serialization:
            includes.add("<format>")
        if self.decl.deprecated or any(field.deprecated for field in self.decl.fields):
            includes.add(quote(Path("pydjinni/deprecated.hpp")))
        return includes

    @property
    def source_includes(self) -> set[str]:
        includes = super().source_includes
        if self.config.string_serialization:
            includes.add("<string>")
            includes.add(quote(Path("pydjinni/format.hpp")))
        return includes

    @property
    def constructor_comment(self):
        return '\n'.join(
            [f"@param {field.cpp.name} {field.cpp.comment}" for field in self.decl.fields if field.comment is not None])


class CppDataField(CppBaseField):
    decl: DataField = Field(exclude=True, repr=False)

    @cached_property
    def type_spec(self): return self._type_specifier(self.decl.type_ref)


class CppFunction(CppBaseType):
    decl: Function = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def typename(self) -> str: return f"std::function<{self._type_specifier(self.decl.return_type_ref)}" \
                                      f"({','.join([self._type_specifier(parameter.type_ref) for parameter in self.decl.parameters])})>"

    @computed_field
    @cached_property
    def by_value(self) -> bool: return False

    @cached_property
    def proxy(self): return "cpp" in self.decl.targets

    @cached_property
    def type_spec(self): return self._type_specifier(self.decl.return_type_ref)

    @cached_property
    def header_includes(self) -> set[str]:
        return super().header_includes | {"<functional>"}

    @cached_property
    def noexcept(self) -> bool: return self.decl.throwing is None


class CppParameter(CppBaseField):
    decl: Parameter = Field(exclude=True, repr=False)

    @cached_property
    def type_spec(self): return self._type_specifier(self.decl.type_ref, is_parameter=True, use_notnull=True)


class CppErrorDomain(CppBaseType):
    decl: ErrorDomain = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def by_value(self) -> bool:
        return False

    @property
    def header_includes(self) -> set[str]:
        includes = super().header_includes | {"<exception>", "<string>", "<utility>"}
        if any(error_code.deprecated for error_code in self.decl.error_codes):
            includes.add(quote(Path("pydjinni/deprecated.hpp")))
        return includes

    class CppErrorCode(CppBaseType):
        @property
        def constructor_comment(self):
            return '\n'.join(
                [f"@param {parameter.cpp.name} {parameter.cpp.comment}" for parameter in self.decl.parameters if
                 parameter.comment is not None])
