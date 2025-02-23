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
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from pydjinni.generator.java.java.comment_renderer import JavaDocCommentRenderer
from pydjinni.generator.java.java.config import JavaConfig
from pydjinni.generator.java.java.keywords import keywords
from pydjinni.generator.validator import validate
from pydjinni.parser.ast import Record, Function, Interface, Parameter
from pydjinni.parser.base_models import BaseType, BaseField, BaseExternalType, TypeReference, DataField
from pydjinni.parser.identifier import IdentifierType as Identifier


def return_type(type_ref: TypeReference | None, asynchronous: bool = False) -> str:
    if type_ref:
        output = data_type(type_ref, boxed=asynchronous)
    else:
        output = "Void" if asynchronous else "void"
    return output


def data_type(type_ref: TypeReference, boxed: bool = False) -> str:
    output = type_ref.type_def.java.boxed if boxed or type_ref.optional else type_ref.type_def.java.typename
    if type_ref.parameters:
        output += f"<{', '.join([data_type(parameter, boxed=True) for parameter in type_ref.parameters])}>"
    return output

def filename(package, name):
    return Path(*package.split('.')) / f"{name}.java"


class JavaExternalType(BaseModel):
    """Java type information"""
    typename: str = None
    boxed: str = ""
    reference: bool = True
    generic: bool = False


class JavaBaseType(BaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: JavaConfig = Field(exclude=True, repr=False)

    @cached_property
    @validate(keywords)
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.type)

    @computed_field
    @cached_property
    def typename(self) -> str: return f"{self.package}.{self.name}"

    @computed_field
    @cached_property
    def boxed(self) -> str: return self.typename

    @computed_field
    @cached_property
    def reference(self) -> bool: return True

    @computed_field
    @cached_property
    def generic(self) -> bool: return False

    @cached_property
    @validate(keywords, separator='.')
    def package(self) -> str:
        return '.'.join(self.config.package + [identifier.convert(self.config.identifier.package) for identifier in
                                               self.decl.namespace])

    @cached_property
    def source(self): return Path(*self.package.split('.')) / f"{self.name}.java"

    @cached_property
    def comment(self):
        return JavaDocCommentRenderer(self.config.identifier).render_tokens(*self.decl.parsed_comment).strip() \
            if self.decl.comment else ''

    @cached_property
    def class_modifier(self):
        output = ""
        if self.config.class_access_modifier == JavaConfig.ClassAccessModifier.public:
            output += "public "
        return output


class JavaBaseField(BaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: JavaConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.field)

    @cached_property
    def comment(self):
        return JavaDocCommentRenderer(self.config.identifier).render_tokens(*self.decl.parsed_comment).strip() \
            if self.decl.comment else ''

    @cached_property
    def data_type(self) -> str: return data_type(self.decl.type_ref)


class JavaRecord(JavaBaseType):
    decl: Record = Field(exclude=True, repr=False)

    @cached_property
    def base_type(self) -> bool:
        return "java" in self.decl.targets

    @cached_property
    def name(self):
        name = self.decl.name
        if self.base_type:
            name += "_base"
        return Identifier(name).convert(self.config.identifier.type)

    @computed_field
    @cached_property
    def typename(self) -> str:
        name = self.decl.name.convert(self.config.identifier.type)
        return f"{self.package}.{name}"

    @cached_property
    def class_modifier(self):
        output = super().class_modifier
        if self.config.use_final_for_record and not self.base_type:
            output += "final "
        return output

class JavaDataField(JavaBaseField):
    @cached_property
    def getter(self):
        return Identifier(f"get_{self.decl.name}").convert(self.config.identifier.method)

    @cached_property
    def field_modifier(self):
        output = ""
        if self.config.use_final_for_record:
            output += "final "
        return output

    @property
    def nullable_annotation(self) -> str:
        return self.config.nullable_annotation if self.decl.type_ref.optional else self.config.nonnull_annotation

    @cached_property
    def hash_code(self) -> str:
        if self.decl.type_ref.optional:
            return f"{self.decl.java.name} == null ? 0 : {self.decl.java.name}.hashCode()"
        elif self.decl.type_ref.type_def.java.typename == self.decl.type_ref.type_def.java.boxed:
            match self.decl.type_ref.type_def.name:
                case "binary":
                    return f"java.util.Arrays.hashCode({self.decl.java.name})"
                case _:
                    return f"{self.decl.java.name}.hashCode()"
        else:
            match self.decl.type_ref.type_def.java.typename:
                case "long":
                    return f"((int) ({self.decl.java.name} ^ ({self.decl.java.name} >>> 32)))"
                case "float":
                    return f"Float.floatToIntBits({self.decl.java.name})"
                case "double":
                    return f"((int) (Double.doubleToLongBits({self.decl.java.name}) ^ (Double.doubleToLongBits({self.decl.java.name}) >>> 32)))"
                case "boolean":
                    return f"({self.decl.java.name} ? 1 : 0)"
                case _:
                    return self.decl.java.name

    @cached_property
    def equals(self) -> str:
        if self.decl.type_ref.optional:
            return f"((this.{self.decl.java.name} == null && other.{self.decl.java.name} == null) | | (this.{self.decl.java.name} != null & & this.{self.decl.java.name}.equals(other.{self.decl.java.name})))"
        elif self.decl.type_ref.type_def.primitive == BaseExternalType.Primitive.enum:
            return f"this.{self.decl.java.name} == other.{self.decl.java.name}"
        elif self.decl.type_ref.type_def.java.typename == self.decl.type_ref.type_def.java.boxed:
            match self.decl.type_ref.type_def.name:
                case "binary":
                    return f"java.util.Arrays.equals({self.decl.java.name}, other.{self.decl.java.name})"
                case _:
                    return f"{self.decl.java.name}.equals(other.{self.decl.java.name})"
        else:
            return f"this.{self.decl.java.name} == other.{self.decl.java.name}"


class JavaFlags(JavaBaseType):
    @computed_field
    @cached_property
    def typename(self) -> str: return f"java.util.EnumSet<{self.package}.{self.name}>"


class JavaFunction(JavaBaseType):
    decl: Function = Field(exclude=True, repr=False)

    @cached_property
    @validate(keywords)
    def name(self) -> str:
        if self.decl.anonymous:
            return self.decl.name.title()
        else:
            return super().name

    @cached_property
    def return_type(self) -> str:
        return return_type(self.decl.return_type_ref)

    @property
    def nullable_annotation(self) -> str:
        return self.config.nullable_annotation if self.decl.return_type_ref.optional else self.config.nonnull_annotation



class JavaSymbolicConstantField(JavaBaseField):
    @computed_field
    @cached_property
    @validate(keywords)
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.enum)


class JavaInterface(JavaBaseType):
    class JavaMethod(JavaBaseField):
        @computed_field
        @cached_property
        @validate(keywords)
        def name(self) -> str: return self.decl.name.convert(self.config.identifier.method)

        @cached_property
        def return_type(self) -> str:
            output = return_type(self.decl.return_type_ref, self.decl.asynchronous)
            if self.decl.asynchronous:
                output = f"java.util.concurrent.CompletableFuture<{output}>"
            return output

        @property
        def nullable_annotation(self) -> str:
            return self.config.nullable_annotation if self.decl.return_type_ref.optional else self.config.nonnull_annotation


        @cached_property
        def callback_type(self) -> str:
            return return_type(self.decl.return_type_ref, self.decl.asynchronous)




class JavaErrorDomain(JavaBaseType):
    pass

    class JavaErrorCode(JavaBaseType):
        pass


@dataclass
class NativeLibLoader:
    config: JavaConfig

    @property
    def name(self):
        return f"Native{self.config.native_lib}Loader"

    @property
    def package(self) -> str:
        return '.'.join(self.config.package + self.config.support_types_package)

    @property
    def native_lib(self) -> str:
        return self.config.native_lib

    @property
    def source(self) -> Path: return filename(self.package, self.name)


@dataclass
class NativeCleaner:
    config: JavaConfig

    @property
    def name(self) -> str:
        return f"NativeCleaner"

    @property
    def package(self) -> str:
        return '.'.join(self.config.package + self.config.support_types_package)

    @property
    def source(self) -> Path: return filename(self.package, self.name)
