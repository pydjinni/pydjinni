from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class GenerateBaseConfig(BaseModel):
    class DerivingType(str, Enum):
        eq = 'eq'
        ord = 'ord'
        str = 'str'
        json = 'json'

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
    default_deriving: list[DerivingType] = Field(
        default=[],
        description="Deriving functionality that should be added to every record by default."
    )
