from pydantic import BaseModel, Field

from pathlib import Path

import dataclasses
from pydantic.dataclasses import dataclass
from enum import Enum


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
