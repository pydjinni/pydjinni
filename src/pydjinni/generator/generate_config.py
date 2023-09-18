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
