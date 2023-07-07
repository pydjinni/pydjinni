from pathlib import Path

import mistletoe
from pydantic import BaseModel

from pydjinni.generator.java.java.comment_renderer import JavaDocCommentRenderer


class JavaExternalType(BaseModel):
    """Java type information"""
    typename: str = None
    boxed: str = ""
    reference: bool = True
    generic: bool = False


class JavaType(JavaExternalType):
    name: str
    source: Path
    package: str
    comment: str | None = None

    @staticmethod
    def create(name: str, package: list[str], comment: str = None, typename: str = None) -> 'JavaType':
        typename = typename or ".".join(package + [name])
        return JavaType(
            typename=typename,
            boxed=typename,
            name=name,
            source=Path().joinpath(*package) / f"{name}.java",
            package=".".join(package),
            comment=mistletoe.markdown(comment, JavaDocCommentRenderer) if comment else '',
        )


class JavaField(BaseModel):
    name: str
    getter: str | None = None
    setter: str | None = None
    comment: str | None = None
