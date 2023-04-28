from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class GenerateBaseConfig(BaseModel):
    list_processed_files: Path = Field(
        default=None,
        description="File that reports all the parsed and generated files. File format is determined by the file extension. "
                    "Supported extensions: `.yaml`, `.yml`, `.json`, `.toml`"
    )
