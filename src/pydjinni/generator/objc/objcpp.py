from pydantic import BaseModel, Field

from pydjinni.generator.generator import BaseConfig
from pydjinni.regex_datatypes import CppTypename, CppNamespace
from pathlib import Path

class ObjCppConfig(BaseConfig):
    namespace: CppNamespace = Field(
        default=None,
        description="The namespace name to use for generated Objective-C++ classes"
    )

class ObjCppType(BaseModel):
    translator: CppTypename
    header: Path

    @classmethod
    def from_name(cls, name: str):
        return cls(
            translator=name.lower(),
            header=Path(name.lower())
        )
