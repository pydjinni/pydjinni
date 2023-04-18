from pathlib import Path

from pydantic import BaseModel, Field


class ObjcppExternalType(BaseModel):
    translator: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$"
    )
    header: Path


class ObjcppType(ObjcppExternalType):
    comment: str | None = None


class ObjcppField(BaseModel):
    name: str
    comment: str | None = None
