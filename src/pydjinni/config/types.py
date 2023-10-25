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

import dataclasses
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


@dataclass
class OutPaths:
    source: Path = dataclasses.field(
        metadata=dict(
            description="The output directory for source files",
        )
    )
    header: Path = dataclasses.field(
        metadata=dict(
            description="The output directory for header files",
        )
    )


class IdentifierStyle(BaseModel):
    class Case(str, Enum):
        none = 'none'
        camel = 'camelCase'
        pascal = 'PascalCase'
        snake = 'snake_case'
        kebab = 'kebab-case'
        train = 'TRAIN_CASE'

    style: Case
    prefix: str = Field(
        default=None,
        description="Prefix that is added to the beginning of the identifier"
    )
