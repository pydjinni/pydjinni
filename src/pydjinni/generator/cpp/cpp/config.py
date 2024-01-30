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

from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator, PlainSerializer, WithJsonSchema

from pydjinni.config.types import OutPaths, IdentifierStyle


class CppIdentifier(BaseModel):
    type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
    file: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
    field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
    namespace: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake


CppNamespace = Annotated[
    str,
    AfterValidator(lambda x: x.split('::')),
    PlainSerializer(lambda x: '::'.join(x), return_type=str),
    WithJsonSchema({'type': 'string', 'pattern': r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))+[a-zA-Z][a-zA-Z0-9_]*$"},
                   mode='validation')
]


class CppConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. "
                    "Separate folders for `source` and `header` files can be specified."
    )
    namespace: CppNamespace | list[str] = Field(
        default=[],
        description="The namespace name to use for generated C++ classes"
    )
    include_prefix: Path = Field(
        default=None,
        description="The prefix for `#includes` of header files from C++ files"
    )
    header_extension: str = Field(
        default="hpp",
        description="The filename extension for C++ header files"
    )
    source_extension: str = Field(
        default="cpp",
        description="The filename extension for C++ files"
    )
    identifier: CppIdentifier = CppIdentifier()
    string_serialization_for_enums: bool = Field(
        default=False,
        description="Whether to generate ostream << overloads for stringifying enums and flags"
    )
