from pathlib import Path

from pydantic import BaseModel, Field

from pydjinni.config.types import OutPaths, IdentifierStyle


class CppIdentifier(BaseModel):
    type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
    file: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
    field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake


class CppConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )
    namespace: str = Field(
        default=None,
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))+[a-zA-Z][a-zA-Z0-9_]*$",
        description="The namespace name to use for generated C++ classes"
    )
    include_prefix: Path = Field(
        default=None,
        description="The prefix for `#includes` of header files from C++ files"
    )
    header_extension: str = Field(
        default="hpp",
        description="The filename extension for C++ header files"
    )
    source_extension: str = Field(
        default="cpp",
        description="The filename extension for C++ files"
    )
    default_record_constructor: bool = Field(
        default=True,
        description="Generate a default constructor for records in C++"
    )
    identifier: CppIdentifier = CppIdentifier()
