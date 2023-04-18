from pathlib import Path

from pydantic import BaseModel, Field

from pydjinni.config.types import OutPaths


class ObjcppConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )
    namespace: str = Field(
        default=None,
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))+[a-zA-Z][a-zA-Z0-9_]*$",
        description="The namespace name to use for generated Objective-C++ classes"
    )
    header_extension: str = Field(
        default="h",
        description="The filename extension for Objective-C++ header files"
    )
    source_extension: str = Field(
        default="mm",
        description="The filename extension for Objective-C++ source files"
    )
