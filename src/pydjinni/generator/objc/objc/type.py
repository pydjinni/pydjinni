from pathlib import Path

from pydantic import BaseModel


class ObjcExternalType(BaseModel):
    typename: str = None
    boxed: str
    header: Path
    pointer: bool = True


class ObjcType(ObjcExternalType):
    swift_typename: str
    comment: str | None = None


class ObjcField(BaseModel):
    name: str
    comment: str | None = None
