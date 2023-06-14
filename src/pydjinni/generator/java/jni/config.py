from pathlib import Path

from pydantic import BaseModel, Field

from pydjinni.config.types import IdentifierStyle, OutPaths


class JniIdentifierStyle(BaseModel):
    file: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
    class_name: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
    field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    namespace: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal


class JniConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )
    namespace: str = Field(
        default=None,
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))+[a-zA-Z][a-zA-Z0-9_]*$",
        description="The namespace name to use for generated JNI C++ classes"
    )
    include_prefix: Path = Field(
        default=None,
        description="The prefix for `#includes` of JNI header files from JNI C++ files."
    )
    include_cpp_prefix: Path = Field(
        default=None,
        description="The prefix for `#includes` of the main header files from JNI C++ files."
    )
    header_extension: str = Field(
        default="hpp",
        description="The filename extension for JNI C++ header files"
    )
    source_extension: str = Field(
        default="cpp",
        description="The filename extension for JNI C++ files"
    )
    loader: bool = Field(
        default=True,
        description="If enabled, a minimal `JNI_OnLoad`/`JNI_OnUnload` implementation is generated."
    )
    identifier: JniIdentifierStyle = JniIdentifierStyle()
