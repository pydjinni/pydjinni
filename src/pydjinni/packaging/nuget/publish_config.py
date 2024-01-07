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

from pydantic import BaseModel, HttpUrl, Field


class NuGetPublishConfig(BaseModel):
    """
    Maven publishing information
    """
    source: HttpUrl | Path = Field(
        default="https://api.nuget.org/v3/index.json",
        description="NuGet server URL or local folder where the package should be published to"
    )
    repository: HttpUrl = Field(
        default=None,
        description="URL to the source Git repository"
    )
    description: str = Field(
        default="",
        description="(short) description of the package."

    )
    readme: Path = Field(
        default=None,
        description="Path to a Markdown Readme file that should be included in the NuGet package."
    )
    net_version: str = Field(
        default="net8.0",
        description=".NET version used to compile the binaries"
    )
    authors: list[str] = Field(
        default=[],
        description="A comma-separated list of packages authors (matching the profile names on nuget.org)"
    )
    username: str = Field(
        default=None,
        description="Username for the NuGet Server"
    )
    password: str = Field(
        default=None,
        description="Password (token) to access the server."
                    "It is recommended to set this via the environment variable "
                    "`PACKAGE__NUGET__PUBLISH__PASSWORD`"
    )
