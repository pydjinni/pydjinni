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

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator, PlainSerializer, WithJsonSchema

from pydjinni.config.types import IdentifierStyle
from pydjinni.parser.identifier import Identifier


class JavaIdentifierStyle(BaseModel):
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
    field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    package: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake


Package = Annotated[
    str,
    AfterValidator(lambda x: x.split('.')),
    PlainSerializer(lambda x: '.'.join(x), return_type=str),
    WithJsonSchema({'type': 'string', 'pattern': r"^[a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_]$"}, mode='validation')
]


class JavaConfig(BaseModel):
    """
    Java configuration options
    """

    out: Path = Field(
        description="The output folder for the generated files."
    )

    class ClassAccessModifier(StrEnum):
        public = 'public'
        package = 'package'

    package: Package | list[Identifier] = Field(
        default=[],
        examples=["my.package.name", "other.package.name"],
        description="The package name to use for generated Java classes"
    )
    interfaces: bool = Field(
        default=False,
        description="Whether Java interfaces should be used instead of abstract classes where possible"
    )
    class_access_modifier: ClassAccessModifier = Field(
        default=ClassAccessModifier.public,
        description="The access modifier to use for generated Java classes",
    )
    cpp_exception: str = Field(
        default="java.lang.RuntimeException",
        pattern=r"^([a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_][.])?[a-zA-Z][a-zA-Z0-9_]*$",
        description="The type for translated C++ exceptions in Java",
    )
    annotation: str = Field(
        default=None,
        pattern=r"^@([a-z][a-z0-9_]*(([.][a-z0-9_]+)+[0-9a-z_])?[.])?[a-zA-Z][a-zA-Z0-9_]*$",
        description="Java annotation to place on all generated Java classes",
        examples=["@Foo"]
    )
    use_final_for_record: bool = Field(
        default=True,
        description="Whether generated Java classes for records should be marked `final`",
    )
    native_lib: str = Field(
        default=None,
        description="Name of the native library containing the JNI interface. "
                    "If this option is set and an interface is marked as `main`, a static block will be "
                    "added to the interface, that loads the native library."
    )
    function_prefix: str = Field(
        default="Functional",
        description="Prefix for generated functional interfaces."
    )
    identifier: JavaIdentifierStyle = JavaIdentifierStyle()
