from pathlib import Path

from pydantic import BaseModel

from pydjinni.parser.base_models import BaseType, BaseExternalType


class ObjcExternalType(BaseModel):
    typename: str = None
    boxed: str
    header: Path
    pointer: bool = True


class ObjcType(ObjcExternalType):
    swift_typename: str
    comment: str | None = None
    init: str = None
    convenience_init: str = None
    source: Path



class ObjcField(BaseModel):
    name: str
    comment: str | None = None
    specifier: str | None = None
    type_decl: str | None = None
