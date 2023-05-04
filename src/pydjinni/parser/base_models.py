from pydantic import BaseModel, Extra

from pydjinni.parser.identifier import Identifier


class BaseExternalType(BaseModel):
    name: str
    comment: str | None = None


class BaseType(BaseModel, extra='allow'):
    name: Identifier
    position: int
    comment: list[str] | None = None


class BaseField(BaseModel, extra='allow'):
    name: Identifier
    position: int
    comment: list[str] | None = None
