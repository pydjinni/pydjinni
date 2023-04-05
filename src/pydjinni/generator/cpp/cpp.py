from pathlib import Path
from pydantic import BaseModel, Field
from pydjinni.generator.generator import BaseConfig

class CppConfig(BaseConfig):
    namespace: str = Field(
        default=None,
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))+[a-zA-Z][a-zA-Z0-9_]*$",
        description="The namespace name to use for generated C++ classes"
    )

class CppType(BaseModel):
    typename: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$",
        description="Must be a valid C++ type identifier",
        examples=[
            "int8_t", "::some::Type"
        ]
    )
    header: Path
    by_value: bool = False

    @classmethod
    def from_name(cls, name: str):
        return cls(
            typename=name.lower(),
            header=Path(name.lower())
        )
