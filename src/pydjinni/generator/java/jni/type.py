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

from pydjinni.generator.cpp.cpp.keywords import keywords as cpp_keywords
from pydjinni.generator.validator import validate

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from pydjinni.generator.java.jni.config import JniConfig
from pydjinni.parser.ast import Interface, Parameter, Function
from pydjinni.parser.base_models import BaseType, BaseField, TypeReference


class NativeType(StrEnum):
    object = 'jobject'
    string = 'jstring'
    boolean = 'jboolean'
    byte = 'jbyte'
    char = 'jchar'
    short = 'jshort'
    int = 'jint'
    long = 'jlong'
    float = 'jfloat'
    double = 'jdouble'
    byte_array = 'jbyteArray'


class JniExternalType(BaseModel):
    translator: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$"
    )
    header: Path
    typename: NativeType = Field(
        default=NativeType.object,
        description="The Java native [`jvalue` union type](https://docs.oracle.com/en/java/javase/17/docs/specs/jni/types.html#the-value-type) as represented in JNI."
    )
    type_signature: str = Field(
        examples=["I"],
        description="[Java VM Type Signatures](https://docs.oracle.com/en/java/javase/17/docs/specs/jni/types.html#type-signatures)"
    )
    boxed_type_signature: str = Field(
        examples=["Ljava/lang/Integer;"],
        description="Type signature of the boxed Java type. If the type is always boxed, both `type_signature` and "
                    "`boxed_type_signature` should contain the same value."
    )


def get_field_accessor(type_ref: TypeReference) -> str:
    native_type = type_ref.type_def.jni.typename
    type = NativeType.object if native_type in [NativeType.string,
                                                NativeType.byte_array] or type_ref.optional else native_type
    return f"Get{type[1:].capitalize()}Field"


def get_typename(type_ref: TypeReference) -> str:
    if type_ref:
        if type_ref.optional and type_ref.type_def.jni.typename not in [NativeType.string, NativeType.byte_array]:
            return NativeType.object
        else:
            return type_ref.type_def.jni.typename
    else:
        return ""


def routine_name(type_ref: TypeReference) -> str:
    if type_ref:
        native_type = type_ref.type_def.jni.typename
        if native_type in [NativeType.string, NativeType.byte_array] or type_ref.optional:
            native_type = NativeType.object
        native_type = native_type[1:].capitalize()
    else:
        native_type = "Void"
    return f"Call{native_type}Method"


def type_signature(parameters: list[Parameter], return_type_ref: TypeReference):
    parameter_type_signatures = ""
    for parameter in parameters:
        if parameter.type_ref.optional:
            parameter_type_signatures += parameter.type_ref.type_def.jni.boxed_type_signature
        else:
            parameter_type_signatures += parameter.type_ref.type_def.jni.type_signature
    return_type_signature = "V"
    if return_type_ref:
        if return_type_ref.optional:
            return_type_signature = return_type_ref.type_def.jni.boxed_type_signature
        else:
            return_type_signature = return_type_ref.type_def.jni.type_signature
    return f"({parameter_type_signatures}){return_type_signature}"


class JniBaseType(BaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: JniConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def translator(self) -> str: return f"::{self.namespace}::{self.name}"

    @computed_field
    @cached_property
    def header(self) -> Path:
        return Path(f"{self.decl.name.convert(self.config.identifier.file)}.{self.config.header_extension}")

    @cached_property
    def source(self) -> Path:
        return Path(f"{self.decl.name.convert(self.config.identifier.file)}.{self.config.source_extension}")

    @computed_field
    @cached_property
    def typename(self) -> NativeType: return NativeType.object

    @computed_field
    @cached_property
    def type_signature(self) -> str: return f"L{self.class_descriptor};"

    @computed_field
    @cached_property
    def boxed_type_signature(self) -> str: return self.type_signature

    @cached_property
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.class_name)

    @cached_property
    def jni_prefix(self) -> str:
        segments = self.decl.java.package.split('.') + [self.name]
        segments = [segment.replace("_", "_1") for segment in segments]
        segments = [segment.replace("$", "_00024") for segment in segments]
        return "_".join(["Java"] + segments)

    @cached_property
    @validate(cpp_keywords, separator="::")
    def namespace(self): return '::'.join(self.config.namespace + [identifier.convert(self.config.identifier.namespace)
                                                                   for identifier in self.decl.namespace])

    @cached_property
    def class_descriptor(self) -> str: return '/'.join(self.decl.java.package.split('.') + [self.name])


class JniFunction(JniBaseType):
    decl: Function = Field(exclude=True, repr=False)

    @cached_property
    def name(self) -> str: return self.decl.name.title() if self.decl.anonymous else super().name

    @cached_property
    def wrapper(self) -> str: return f"{self.name}Wrapper"

    @cached_property
    def routine_name(self) -> str: return routine_name(self.decl.return_type_ref)

    @cached_property
    def type_signature(self) -> str: return type_signature(self.decl.parameters, self.decl.return_type_ref)

    @cached_property
    def return_type_spec(self) -> str:
        return self.decl.return_type_ref.type_def.jni.typename if self.decl.return_type_ref else "void"


class JniBaseField(BaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: JniConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.field)


class JniSymbolicConstantField(JniBaseField):
    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.enum)


class JniInterface(JniBaseType):
    class JniMethod(JniBaseField):
        decl: Interface.Method = Field(exclude=True, repr=False)

        @computed_field
        @cached_property
        def name(self) -> str:
            return self.decl.name.convert(self.config.identifier.method)

        @cached_property
        def type_signature(self) -> str: return type_signature(self.decl.parameters, self.decl.return_type_ref)

        @cached_property
        def routine_name(self) -> str: return routine_name(self.decl.return_type_ref)

        @cached_property
        def return_type_spec(self) -> str:
            return self.decl.return_type_ref.type_def.jni.typename if self.decl.return_type_ref else "void"


class JniParameter(JniBaseField):
    decl: Parameter = Field(exclude=True, repr=False)

    @cached_property
    def field_accessor(self): return get_field_accessor(self.decl.type_ref)

    @cached_property
    def typename(self): return get_typename(self.decl.type_ref)


class JniRecord(JniBaseType):
    class JniField(JniBaseField):
        @cached_property
        def field_accessor(self): return get_field_accessor(self.decl.type_ref)

        @cached_property
        def typename(self): return get_typename(self.decl.type_ref)
