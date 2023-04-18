from pathlib import Path

from pydantic import BaseModel, Field


class CppExternalType(BaseModel):
    typename: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$",
        description="Must be a valid C++ type identifier",
        examples=[
            "int8_t", "::some::Type"
        ]
    )
    header: Path
    by_value: bool = False


class CppType(CppExternalType):
    source: Path
    includes: list[Path]
    comment: str | None = None


class CppField(BaseModel):
    name: str
    comment: str | None = None
