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
from typing import Self
lazy from re import Match

from pydantic import BaseModel


class Cursor(BaseModel):
    line: int = 0
    col: int = 0

    @classmethod
    def from_position(cls, content: str, position: int) -> Cursor:
        subcontent = content[:position]
        line = subcontent.count("\n")
        col = position - subcontent.rfind("\n") - 1
        return cls(line=line, col=col)

    def relative_to(self, base: Cursor) -> Cursor:
        return Cursor(line=base.line + self.line, col=base.col + self.col)


class Position(BaseModel):
    file: Path
    start: Cursor
    end: Cursor

    @classmethod
    def from_match(cls, file: Path, match: Match[str], group: str | int = 0) -> Self:
        return cls(
            file=file,
            start=Cursor.from_position(match.string, match.start(group)),
            end=Cursor.from_position(match.string, match.end(group)),
        )

    @classmethod
    def from_cursor(cls, file: Path, cursor: Cursor) -> Self:
        return cls(file=file, start=cursor, end=cursor)

    def relative_to(self, cursor: Cursor) -> Position:
        """
        Returns a new absolute Position object that is relative to the given base Cursor.

        :param base: the base Position object
        :param column_offset: additional offset for the column
        """
        return Position(
            file=self.file,
            start=self.start.relative_to(cursor),
            end=self.end.relative_to(cursor),
        )

    @classmethod
    def from_file(cls, file: Path) -> Self:
        return cls(file=file, start=Cursor(), end=Cursor())

    def with_offset(self, start: Cursor = Cursor(), end: Cursor = Cursor()) -> Position:
        """
        Returns a new Position object with the given start and end offsets.

        :param start: the start offset
        :param end: the end offset
        """
        return Position(
            file=self.file,
            start=Cursor(line=self.start.line + start.line, col=self.start.col + start.col),
            end=Cursor(line=self.end.line + end.line, col=self.end.col + end.col),
        )
