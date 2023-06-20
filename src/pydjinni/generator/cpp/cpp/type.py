from pathlib import Path

from pydantic import BaseModel, Field


class CppExternalType(BaseModel):
    typename: str = Field(
        description="Must be a valid C++ type identifier",
        examples=[
            "int8_t", "::some::Type"
        ]
    )
    header: Path
    by_value: bool = False


class CppType(CppExternalType):
    name: str
    source: Path
    comment: str | None
    namespace: str
    proxy: bool = False


class CppField(BaseModel):
    name: str
    comment: str | None
    type_spec: str | None
