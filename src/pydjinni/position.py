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
from re import Match

from pydantic import BaseModel


class Cursor(BaseModel):
    line: int = 0
    col: int = 0


class Position(BaseModel):
    start: Cursor | None = None
    end: Cursor | None = None
    file: Path | None = None

    @staticmethod
    def from_match(content: str, file: Path, match: Match, group: str | int = 1):
        line_start = content[:match.start(group)].count('\n')
        line_end = content[:match.end(group)].count('\n')
        col_start = match.start(group) - content.rfind('\n', 0, match.start(group)) - 1
        col_end = match.end(group) - content.rfind('\n', 0, match.end(group)) - 1
        return Position(file=file, start=Cursor(line=line_start, col=col_start), end=Cursor(line=line_end, col=col_end))
    
    def relative_to(self, base: 'Position', column_offset: int = 0):
        """
        Returns a new absolute Position object that is relative to the given base Position.

        :param base: the base Position object
        :param column_offset: additional offset for the column
        """
        return Position(
            start=Cursor(
                line=base.start.line + self.start.line,
                col=base.start.col + self.start.col + column_offset
            ), 
            end=Cursor(
                line=base.start.line + self.end.line,
                col=base.start.col + self.end.col + column_offset
            ),
            file=self.file
        )
    
    def with_offset(self, start: Cursor = Cursor(), end: Cursor = Cursor()):
        """
        Returns a new Position object with the given start and end offsets.

        :param start: the start offset
        :param end: the end offset
        """
        return Position(
            start=Cursor(line=self.start.line + start.line, col=self.start.col + start.col),
            end=Cursor(line=self.end.line + end.line, col=self.end.col + end.col),
            file=self.file
        )
