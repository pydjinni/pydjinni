from pydantic import BaseModel, Field

from pydjinni.generator.generator import BaseConfig
from pathlib import Path

class ObjCppConfig(BaseConfig):
    namespace: str = Field(
        default=None,
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))+[a-zA-Z][a-zA-Z0-9_]*$",
        description="The namespace name to use for generated Objective-C++ classes"
    )

class ObjCppType(BaseModel):
    translator: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$"
    )
    header: Path

    @classmethod
    def from_name(cls, name: str):
        return cls(
            translator=name.lower(),
            header=Path(name.lower())
        )
