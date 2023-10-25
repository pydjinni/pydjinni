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

from pydjinni.config.types import OutPaths
from pydjinni.generator.cpp.cpp.config import CppNamespace
from pydjinni.parser.identifier import Identifier


class ObjcppConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )
    namespace: CppNamespace | list[Identifier] = Field(
        default=[],
        description="The namespace name to use for generated Objective-C++ classes"
    )
    header_extension: str = Field(
        default="h",
        description="The filename extension for Objective-C++ header files"
    )
    source_extension: str = Field(
        default="mm",
        description="The filename extension for Objective-C++ source files"
    )
