from pathlib import Path

from pydantic import Field, BaseModel


class ConanConfigModel(BaseModel):
    """Settings specific to the Conan build strategy"""
    profiles: Path = Field(
        default=Path("profiles"),
        description="The base directory where the target profiles are located"
    )
