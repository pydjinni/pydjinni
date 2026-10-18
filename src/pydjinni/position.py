# Copyright 2023 - 2025 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
from typing import ClassVar, Final, Self
lazy from re import Match

from pydantic import BaseModel, ConfigDict, field_validator


class Cursor(BaseModel):
    """The cursor position inside a file. Both ``line`` and ``col`` are starting from 0."""

    model_config = ConfigDict(frozen=True)

    line: int = 0
    col: int = 0

    @classmethod
    def from_index(cls, content: str, index: int) -> Cursor:
        r"""Convert a position index on a string to a Cursor with line/col information.

        Every `\n` character inside the ``content` is treated as a new line in the returned Cursor.

        Args:
            content: the input string
            index: linear index position inside of the string

        Returns:
            Cursor: the cursor derived from the index position
        """
        assert index >= 0 and index <= len(content), "Index must be in range of given content string"
        subcontent: Final = content[:index]
        return cls(
            line=subcontent.count("\n"),
            col=index - subcontent.rfind("\n") - 1,
        )

    def relative_to(self, cursor: Cursor) -> Cursor:
        """Returns a new Cursor with the ``cursor`` applied as a vector."""
        return Cursor(
            line=cursor.line + self.line,
            col=cursor.col + self.col,
        )


class Position(BaseModel):
    """Represents a range inside of a file."""

    model_config = ConfigDict(frozen=True)

    null_cursor: ClassVar[Cursor] = Cursor()

    file: Path
    start: Cursor
    end: Cursor

    @field_validator("start", "end")
    @classmethod
    def _validate_cursor_coordinates(cls, cursor: Cursor) -> Cursor:
        if cursor.line < 0 or cursor.col < 0:
            raise ValueError("Position cursors must have non-negative line and column values")
        return cursor

    @classmethod
    def from_match(cls, file: Path, match: Match[str], group: str | int = 0) -> Self:
        """Return a new Position object from a RegEx Match object.

        Args:
            file: source file
            match: RegEx Match to extract the position from
            group: the group for which the position should be returned
        """
        return cls(
            file=file,
            start=Cursor.from_index(match.string, match.start(group)),
            end=Cursor.from_index(match.string, match.end(group)),
        )

    @classmethod
    def from_cursor(cls, file: Path, cursor: Cursor) -> Self:
        """Return a zero-width Position object at ``cursor``."""
        return cls(
            file=file,
            start=cursor,
            end=cursor,
        )

    @classmethod
    def from_file(cls, file: Path) -> Self:
        """Return a new Position object pointing to a file, without specific Cursor information.

        Args:
            file: the file location
        """
        return cls(
            file=file,
            start=cls.null_cursor,
            end=cls.null_cursor,
        )

    def relative_to(self, cursor: Cursor) -> Position:
        """Return a new absolute Position object that is relative to the given base Cursor.

        Args:
            cursor: the vector applied to both start and end positions
        """
        return Position(
            file=self.file,
            start=self.start.relative_to(cursor),
            end=self.end.relative_to(cursor),
        )

    def with_offset(self, start: Cursor | None = None, end: Cursor | None = None) -> Position:
        """Return a new Position object with the given start and/or end offsets.

        Args:
            start: the start offset
            end: the end offset
        """
        return Position(
            file=self.file,
            start=self.start.relative_to(start or self.null_cursor),
            end=self.end.relative_to(end or self.null_cursor),
        )
