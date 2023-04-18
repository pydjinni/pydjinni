from pathlib import Path

from pydantic import BaseModel


class ObjcExternalType(BaseModel):
    typename: str
    boxed: str
    header: Path
    pointer: bool = True


class ObjcType(ObjcExternalType):
    comment: str | None = None


class ObjcField(BaseModel):
    name: str
    comment: str | None = None
