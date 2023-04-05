from pydantic import BaseModel, Field
from pathlib import Path

from pydjinni.generator.generator import BaseConfig


class ObjcConfig(BaseConfig):
    type_prefix: str = Field(
        default = None,
        description="The prefix for Objective-C data types (usually two or three letters)"
    )

class ObjcType(BaseModel):
    typename: str
    boxed: str
    header: Path
    pointer: bool = True

    @classmethod
    def from_name(cls, name: str):
        return cls(
            typename=name.lower(),
            boxed=name.lower(),
            header=Path(name.lower())
        )
