from pathlib import Path

from pydantic import Field, BaseModel

from pydjinni.config.types import OutPaths, IdentifierStyle


class ObjcIdentifierStyle(BaseModel):
    file: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    param: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    local: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel


class ObjcConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )
    type_prefix: str = Field(
        default=None,
        description="The prefix for Objective-C data types (usually two or three letters)"
    )
    header_extension: str = Field(
        default="h",
        description="The filename extension for Objective-C header files."
    )
    swift_bridging_header: Path = Field(
        default=None,
        description="The name of the Objective-C Bridging Header required for using the interface from Swift."
    )
    identifier: ObjcIdentifierStyle = ObjcIdentifierStyle()
