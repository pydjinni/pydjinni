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

from pathlib import Path

from pydantic import BaseModel, Field

from pydjinni.config.types import OutPaths, IdentifierStyle
from pydjinni.generator.cpp.cpp.config import CppNamespace


class CppCliIdentifierStyle(BaseModel):
    type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    type_param: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    property: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    local: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    const: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
    file: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    namespace: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal


class CppCliConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. "
                    "Separate folders for `source` and `header` files can be specified."
    )
    namespace: CppNamespace | list[str] = Field(
        default=[],
        description="The namespace name to use for generated C++/CLI classes"
    )
    include_cpp_prefix: Path = Field(
        default=None,
        description="The prefix for `#includes` of header files from C++ files"
    )
    identifier: CppCliIdentifierStyle = CppCliIdentifierStyle()
