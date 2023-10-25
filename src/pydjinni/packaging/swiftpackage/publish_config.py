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

from pydantic import BaseModel, HttpUrl, Field


class SwiftpackagePublishConfig(BaseModel):
    repository: HttpUrl = Field(
        description="Http Url to git repository",
        examples=[
            "https://github.com/foo/bar.git"
        ]
    )
    branch: str = Field(
        default="main",
        description="Git repository branch that the package should be pushed to."
    )
    username: str = Field(
        default=None,
        description="Username of git repository"
    )
    password: str = Field(
        default=None,
        description="Password (token) to access the git repository."
                    "It is recommended to set this via the environment variable "
                    "`PACKAGE__SWIFTPACKAGE__PUBLISH__PASSWORD`"
    )
