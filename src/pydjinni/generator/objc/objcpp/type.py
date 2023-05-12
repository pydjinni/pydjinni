from pathlib import Path

from pydantic import BaseModel, Field


class ObjcppExternalType(BaseModel):
    translator: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$"
    )
    header: Path


class ObjcppType(ObjcppExternalType):
    namespace: str
    name: str
    source: Path


class ObjcppField(BaseModel):
    name: str
