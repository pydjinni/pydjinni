from pathlib import Path

from pydantic import BaseModel, Field

from pydjinni.packaging.configuration import Configuration


class PackageBaseConfig(BaseModel):
    """
    Packaging configuration
    """
    out: Path = Field(
        default=Path("dist"),
        description="output base directory for the final distributable packages"
    )
    target: str = Field(
        description="Name of the target that is going to produce the output"
    )
    build_strategy: str = Field(
        default="conan",
        description="Build system that should be used for compiling"
    )
    version: str = Field(
        default="0.0.0",
        description="Version of the produced package"
    )
    configuration: Configuration = Field(
        default=Configuration.release
    )
