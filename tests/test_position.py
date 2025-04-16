# Copyright 2025 jothepro
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
import re

import pytest
from pydjinni.position import Cursor, Position


@pytest.mark.parametrize(
    "text,cursor_start,cursor_end",
    [
        (
            "find a **match** in this text",
            Cursor(line=0, col=9),
            Cursor(line=0, col=14),
        ),
        (
            "find a\n**match** in the second line\nof a text",
            Cursor(line=1, col=2),
            Cursor(line=1, col=7),
        ),
    ],
)
def test_position_from_match(text, cursor_start, cursor_end):
    match = re.compile(r"(match)", flags=re.MULTILINE).search(text)
    position = Position.from_match(text, Path("test.txt"), match)
    assert position.start == cursor_start
    assert position.end == cursor_end


def test_position_relative_to():
    base = Position(file=Path("test.pydjinni"), start=Cursor(line=1, col=2), end=Cursor(line=1, col=7))
    position = Position(file=Path("test.pydjinni"), start=Cursor(line=2, col=2), end=Cursor(line=3, col=10))
    absolute_position = position.relative_to(base)

    assert absolute_position.start == Cursor(line=3, col=4)
    assert absolute_position.end == Cursor(line=4, col=12)


def test_position_relative_to_column_offset():
    base = Position(file=Path("test.pydjinni"), start=Cursor(line=1, col=2), end=Cursor(line=1, col=7))
    position = Position(file=Path("test.pydjinni"), start=Cursor(line=2, col=2), end=Cursor(line=3, col=10))
    absolute_position = position.relative_to(base, column_offset=1)

    assert absolute_position.start == Cursor(line=3, col=5)
    assert absolute_position.end == Cursor(line=4, col=13)


def test_position_with_offset():
    # GIVEN a base position
    base = Position(file=Path("test.pydjinni"), start=Cursor(line=1, col=2), end=Cursor(line=1, col=7))

    # WHEN applying an offset
    position = base.with_offset(start=Cursor(col=3))

    # THEN the resulting position should have the correct offset
    assert position.start == Cursor(line=1, col=5)
    assert position.end == Cursor(line=1, col=7)
