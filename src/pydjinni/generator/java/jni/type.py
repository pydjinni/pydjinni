from pathlib import Path

from pydantic import BaseModel, Field


class JniExternalType(BaseModel):
    translator: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$"
    )
    header: Path
    typename: str = 'jobject'
    type_signature: str = Field(
        pattern=r'^(\((\[?[ZBCSIJFD]|(L([a-z][a-z0-9]*/)*[A-Z][a-zA-Z0-9]*);)*\))?(\[?[ZBCSIJFD]|(L([a-z][a-z0-9]*/)*[A-Z][a-zA-Z0-9]*);)?$',
        examples=["(ILjava/lang/String;[I)J"]
    )


class JniType(JniExternalType):
    namespace: str
    source: Path
    comment: str | None = None


class JniField(BaseModel):
    name: str
    comment: str | None = None
