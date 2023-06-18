from pathlib import Path

from pydantic import BaseModel, Field


class JavaExternalType(BaseModel):
    """Java type information"""
    typename: str = Field(
        default=None
    )
    boxed: str = Field()
    reference: bool = True
    generic: bool = False


class JavaType(JavaExternalType):
    name: str
    source: Path
    package: str
    comment: str | None = None


class JavaField(BaseModel):
    name: str
    getter: str | None = None
    setter: str | None = None
    comment: str | None = None
