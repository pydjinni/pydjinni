from pydantic import Field

from pydjinni.generator.generator import BaseConfig, BaseType
from pathlib import Path

class JniConfig(BaseConfig):
    namespace: str = Field(
        default=None,
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))+[a-zA-Z][a-zA-Z0-9_]*$",
        description="The namespace name to use for generated JNI C++ classes"
    )

class JniType(BaseType):
    translator: str = Field(
        pattern=r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$"
    )
    header: Path
    typename: str = 'jobject'
    type_signature: str = Field(
        pattern=r'^(\((\[?[ZBCSIJFD]|(L([a-z][a-z0-9]*/)*[A-Z][a-zA-Z0-9]*);)*\))?(\[?[ZBCSIJFD]|(L([a-z][a-z0-9]*/)*[A-Z][a-zA-Z0-9]*);)?$',
        examples=["(ILjava/lang/String;[I)J"]
    )

    @classmethod
    def from_name(cls, name: str):
        return cls(
            translator=name.lower(),
            header=Path(name.lower()),
            type_signature='(ILjava/lang/String;[I)J'
        )


