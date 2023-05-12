from pydantic import BaseModel, Field

from pydjinni.parser.identifier import Identifier


class BaseExternalType(BaseModel):
    name: str
    namespace: str = Field(
        default="",
        pattern="[_\.\w]+"
    )
    comment: str | None = None


class BaseType(BaseModel, extra='allow'):
    name: Identifier
    position: int
    namespace: list[Identifier] = []
    comment: list[str] | None = None


class BaseField(BaseModel, extra='allow'):
    name: Identifier
    position: int
    comment: list[str] | None = None
