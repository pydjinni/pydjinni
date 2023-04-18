from pydantic import BaseModel, Extra

from pydjinni.parser.identifier import Identifier


class BaseExternalType(BaseModel):
    name: Identifier
    comment: str | None = None


class BaseType(BaseModel, extra=Extra.allow):
    name: Identifier
    comment: str | None = None


class BaseField(BaseModel, extra=Extra.allow):
    name: Identifier
    comment: str | None = None
