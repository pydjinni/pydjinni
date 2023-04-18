from pathlib import Path

from pydantic import BaseModel, Field


class JavaExternalType(BaseModel):
    """Java type information"""
    typename: str = Field(
        default=None,
        pattern=r"^[a-z]*$"
    )
    boxed: str = Field(
        pattern=r"^([a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_][.])?[a-zA-Z][a-zA-Z0-9_]*$"
    )
    reference: bool = True
    generic: bool = False


class JavaType(JavaExternalType):
    source: Path
    comment: str | None = None


class JavaField(BaseModel):
    name: str
    comment: str | None = None
