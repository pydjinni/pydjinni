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

import re
from pathlib import Path
from textwrap import dedent

import pytest
from pydantic import ValidationError

from pydjinni.position import Cursor, Position


@pytest.mark.parametrize(
    "index,expected_cursor",
    (
        (0, Cursor(line=0, col=0)),
        (6, Cursor(line=2, col=1)),
        (2, Cursor(line=1, col=1)),
    ),
)
def test_cursor_from_index(index: int, expected_cursor: Cursor):
    # GIVEN a mutliline input string
    content = dedent(
        """
        foo
        bar
        baz
        """
    )

    # WHEN calculating the cursor at a given index
    cursor = Cursor.from_index(content, index)

    # THEN the correct Cursor should be returned
    assert cursor == expected_cursor


@pytest.mark.parametrize("index", (-1, 22))
def test_cursor_from_invalid_index(index: int):
    # GIVEN an invalid index input
    # WHEN trying to calculate the cursor
    # THEN an AssertionError should be raised
    with pytest.raises(AssertionError, match="Index must be in range of given content string"):
        Cursor.from_index("foo", index)


def test_cursor_relative_to():
    # GIVEN a base cursor
    cursor = Cursor(line=4, col=22)

    # WHEN applying another cursor
    new_cursor = cursor.relative_to(Cursor(line=1, col=1))

    # THEN it should be added to the existing cursor
    assert new_cursor == Cursor(line=5, col=23)


def test_position_immutablity():
    # GIVEN a Position object
    position = Position(
        file=Path("foo.baz"),
        start=Cursor(line=4, col=22),
        end=Cursor(line=5, col=0),
    )

    # WHEN trying to change any attribute of the Position
    # THEN a ValidationError should be raised because the instance is frozen
    with pytest.raises(ValidationError, match="Instance is frozen"):
        position.start = Cursor(line=0, col=2)


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
def test_position_from_match(text: str, cursor_start: Cursor, cursor_end: Cursor):
    match = re.compile(r"(match)", flags=re.MULTILINE).search(text)
    assert match
    path = Path("test.txt")
    position = Position.from_match(path, match)
    assert position.file == path
    assert position.start == cursor_start
    assert position.end == cursor_end


def test_position_from_cursor():
    path = Path("test.pydjinni")
    # GIVEN a single Cursor
    cursor = Cursor(line=5, col=8)

    # WHEN creating a Position from the single cursor
    position = Position.from_cursor(path, cursor)

    # THEN both start and end should have the same cursor
    assert position.file == path
    assert position.start == cursor
    assert position.end == cursor


def test_position_from_file():
    # GIVEN just a file path
    path = Path("foo.bar")

    # WHEN creating a Position without cursor information
    position = Position.from_file(path)

    # THEN both cursors should point to 0/0
    assert position.file == path
    assert position.start == Cursor(line=0, col=0)
    assert position.end == Cursor(line=0, col=0)


def test_position_relative_to():
    path = Path("test.pydjinni")
    # GIVEN a cursor vector
    cursor = Cursor(line=1, col=2)
    # AND GIVEN a Position
    position = Position(
        file=path,
        start=Cursor(line=2, col=2),
        end=Cursor(line=3, col=10),
    )

    # WHEN applying the cursor vector
    new_position = position.relative_to(cursor)

    # THEN the cursor should be added to both the start and end cursors
    assert new_position.file == path
    assert new_position.start == Cursor(line=3, col=4)
    assert new_position.end == Cursor(line=4, col=12)


def test_position_with_offset():
    # GIVEN a base position
    base = Position(file=Path("test.pydjinni"), start=Cursor(line=1, col=2), end=Cursor(line=1, col=7))

    # WHEN applying an offset
    position = base.with_offset(start=Cursor(col=3))

    # THEN the resulting position should have the correct offset
    assert position.start == Cursor(line=1, col=5)
    assert position.end == Cursor(line=1, col=7)
