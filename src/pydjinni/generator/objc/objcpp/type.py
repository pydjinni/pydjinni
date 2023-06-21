from pathlib import Path

from pydantic import BaseModel, Field


class ObjcppExternalType(BaseModel):
    translator: str
    header: Path


class ObjcppType(ObjcppExternalType):
    namespace: str
    name: str
    source: Path


class ObjcppField(BaseModel):
    name: str
