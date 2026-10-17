from enum import Enum, Flag, auto
from typing import NamedTuple

lazy from pydjinni.position import Position


class Diagnostic(NamedTuple):
    class Severity(Enum):
        error = auto()
        warning = auto()
        info = auto()
        hint = auto()

    class Tag(Flag):
        unnecessary = auto()
        deprecated = auto()

    class RelatedInformation(NamedTuple):
        position: Position | None
        description: str

    position: Position | None
    description: str
    severity: Severity
    tags: Flag = Tag(0)
    related_information: tuple[RelatedInformation, ...] = ()
