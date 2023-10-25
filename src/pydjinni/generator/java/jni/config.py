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

from pydantic import BaseModel, Field

from pydjinni.config.types import IdentifierStyle, OutPaths
from pydjinni.generator.cpp.cpp.config import CppNamespace
from pydjinni.parser.identifier import Identifier


class JniIdentifierStyle(BaseModel):
    file: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
    class_name: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
    field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    namespace: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal


class JniConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )
    namespace: CppNamespace | list[Identifier] = Field(
        default=[],
        description="The namespace name to use for generated JNI C++ classes"
    )
    include_prefix: Path = Field(
        default=None,
        description="The prefix for `#includes` of JNI header files from JNI C++ files."
    )
    include_cpp_prefix: Path = Field(
        default=None,
        description="The prefix for `#includes` of the main header files from JNI C++ files."
    )
    header_extension: str = Field(
        default="hpp",
        description="The filename extension for JNI C++ header files"
    )
    source_extension: str = Field(
        default="cpp",
        description="The filename extension for JNI C++ files"
    )
    loader: bool = Field(
        default=True,
        description="If enabled, a minimal `JNI_OnLoad`/`JNI_OnUnload` implementation is generated."
    )
    identifier: JniIdentifierStyle = JniIdentifierStyle()
