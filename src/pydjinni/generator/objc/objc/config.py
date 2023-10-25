# Copyright 2023 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

from pydantic import Field, BaseModel

from pydjinni.config.types import OutPaths, IdentifierStyle


class ObjcIdentifierStyle(BaseModel):
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    param: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    local: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel


class SwiftConfig(BaseModel):
    """Configuration options related to using the Objective-C interface from Swift"""
    rename_interfaces: bool = Field(
        default=True,
        description="Whether the Objective-C interface should be annotated with improved Swift method and class names."
    )
    bridging_header: Path = Field(
        default=None,
        description="The name of the Objective-C Bridging Header required for using the interface from Swift."
    )


class ObjcConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )
    type_prefix: str = Field(
        default='',
        description="The prefix for Objective-C data types (usually two or three letters)."
    )
    header_extension: str = Field(
        default="h",
        description="The filename extension for Objective-C header files."
    )
    source_extension: str = Field(
        default="m",
        description="The filename extension for Objective-C source files."
    )
    swift_bridging_header: Path = Field(
        default=None,
        description="The name of the Objective-C Bridging Header required for using the interface from Swift."
    )
    strict_protocols: bool = Field(
        default=False,
        description="All generated `@protocol` will implement `<NSObject>`"
    )
    swift: SwiftConfig = SwiftConfig()
    identifier: ObjcIdentifierStyle = ObjcIdentifierStyle()
