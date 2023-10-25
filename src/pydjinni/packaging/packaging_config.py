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

from pydjinni.packaging.configuration import Configuration


class PackageBaseConfig(BaseModel):
    """
    Packaging configuration
    """
    out: Path = Field(
        default=Path("dist"),
        description="output base directory for the final distributable packages"
    )
    target: str = Field(
        description="Name of the target that is going to produce the output"
    )
    build_strategy: str = Field(
        default="conan",
        description="Build system that should be used for compiling"
    )
    version: str = Field(
        default="0.0.0",
        description="Version of the produced package"
    )
    configuration: Configuration = Field(
        default=Configuration.release
    )
