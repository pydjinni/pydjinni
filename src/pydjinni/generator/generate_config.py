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

from pydjinni.parser.ast import Record


class GenerateBaseConfig(BaseModel):
    "Configuration options related to language gluecode generation"
    list_processed_files: Path = Field(
        default=None,
        description="File that reports all the parsed and generated files. "
                    "File format is determined by the file extension. "
                    "Supported extensions: `.yaml`, `.yml`, `.json`, `.toml`"
    )
    include_dirs: list[Path] = Field(
        default=[],
        description="Include directories that are searched for `@import` and `@extern` directives."
    )
    default_deriving: set[Record.Deriving] = Field(
        default=[],
        description="Deriving functionality that should be added to every record by default."
    )
    support_lib_sources: bool = Field(
        default=True,
        description="Whether the required support lib sources should be copied to the generated output."
    )
