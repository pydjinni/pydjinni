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
from pathlib import PurePosixPath

from pydantic import BaseModel, Field, computed_field

from pydjinni.generator.java.java.comment_renderer import JavaDocCommentRenderer
from pydjinni.generator.java.java.config import JavaConfig
from pydjinni.generator.java.java.keywords import keywords
from pydjinni.generator.validator import validate
from pydjinni.parser.ast import Record, Function
from pydjinni.parser.base_models import BaseType, BaseField, BaseExternalType, TypeReference, DataField
from pydjinni.parser.identifier import IdentifierType as Identifier



def filename(package, name):
    return PurePosixPath(*package.split('.')) / f"{name}.java"


class JavaExternalType(BaseModel):
    """Java type information"""
    typename: str = None
    boxed: str = ""
    reference: bool = True
    generic: bool = False


def apply_type_annotation(type_input: str, annotation: str) -> str:
    if annotation:
        split_output = type_input.rsplit('.', maxsplit=1)
        if len(split_output) == 2:
            package, typename = split_output
            return f"{package}.{annotation} {typename}"
        else:
            return f"{annotation} {type_input}"
    else:
        return type_input


class JavaBase(BaseModel):
    config: JavaConfig = Field(exclude=True, repr=False)

    def compute_return_type(self, type_ref: TypeReference | None, asynchronous: bool = False) -> str:
        if type_ref:
            output = self.compute_data_type(type_ref, boxed=asynchronous)
        else:
            output = "Void" if asynchronous else "void"
        if asynchronous:
            output = apply_type_annotation(f"java.util.concurrent.CompletableFuture", self.config.nonnull_annotation) + f"<{output}>"
        return output

    def compute_data_type(self, type_ref: TypeReference, boxed: bool = False) -> str:
        output = type_ref.type_def.java.boxed if boxed or type_ref.optional else type_ref.type_def.java.typename
        if type_ref.optional:
            output = apply_type_annotation(output, self.config.nullable_annotation)
        else:
            output = apply_type_annotation(output, self.config.nonnull_annotation)
        if type_ref.parameters:
            output += f"<{', '.join([self.compute_data_type(parameter, boxed=True) for parameter in type_ref.parameters])}>"
        return output

class JavaBaseType(JavaBase):
    decl: BaseType = Field(exclude=True, repr=False)

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
    def source(self): return PurePosixPath(*self.package.split('.')) / f"{self.name}.java"

    @cached_property
    def comment(self):
        return JavaDocCommentRenderer(self.config.identifier).render_tokens(*self.decl._parsed_comment).strip() \
            if self.decl._parsed_comment else ''

    @cached_property
    def class_modifier(self):
        output = ""
        if self.config.class_access_modifier == JavaConfig.ClassAccessModifier.public:
            output += "public "
        return output


class JavaBaseField(JavaBase):
    decl: BaseField = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.field)

    @cached_property
    def comment(self):
        return JavaDocCommentRenderer(self.config.identifier).render_tokens(*self.decl._parsed_comment).strip() \
            if self.decl._parsed_comment else ''

    @cached_property
    def data_type(self) -> str: return self.compute_data_type(self.decl.type_ref)


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
        return self.compute_return_type(self.decl.return_type_ref)


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
            return self.compute_return_type(self.decl.return_type_ref, self.decl.asynchronous)


        @cached_property
        def callback_type(self) -> str:
            return self.compute_return_type(self.decl.return_type_ref, self.decl.asynchronous)




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
    def source(self) -> PurePosixPath: return filename(self.package, self.name)


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
    def source(self) -> PurePosixPath: return filename(self.package, self.name)
