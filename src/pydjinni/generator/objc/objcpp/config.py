from pathlib import Path

from pydantic import BaseModel, Field

from pydjinni.config.types import OutPaths
from pydjinni.generator.cpp.cpp.config import CppNamespace
from pydjinni.parser.identifier import Identifier


class ObjcppConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )
    namespace: CppNamespace | list[Identifier] = Field(
        default=[],
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
