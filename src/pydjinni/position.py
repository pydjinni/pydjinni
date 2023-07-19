from pathlib import Path

from pydantic import BaseModel


class Cursor(BaseModel):
    line: int = 0
    col: int = 0


class Position(BaseModel):
    start: Cursor = None
    end: Cursor = None
    file: Path = None
