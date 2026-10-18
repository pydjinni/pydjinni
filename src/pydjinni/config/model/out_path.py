from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class OutPaths(BaseModel):
    """Distinct source and header paths for the generated output."""

    source: Path = Field(description="The output directory for source files")
    header: Path = Field(description="The output directory for header files")


class SingleOutPath(Path):
    """A single output path used for both source and header files."""

    @property
    def source(self) -> Path:
        """The source output directory represented by this path."""
        return self

    @property
    def header(self) -> Path:
        """The header output directory represented by this path."""
        return self

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(Path))


OutPathsLike = SingleOutPath | OutPaths
