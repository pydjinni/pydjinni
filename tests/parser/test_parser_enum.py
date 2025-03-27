# Copyright 2023 jothepro
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

from pydjinni.parser.ast import Enum

from test_parser import given, when


def test_parsing_enum(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = enum {
            first_item;
            second_item;
        }
        """
    )

    enum = when(parser, Enum, "foo")

    items = enum.items

    # THEN the resulting enum should have exactly two items
    assert len(items) == 2
    assert items[0].name == "first_item"
    assert items[1].name == "second_item"


def test_parsing_enum_comment(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            # this is an enum
            foo = enum {
                # with comments
                first_item;
            }
            """
    )

    # WHEN parsing the input
    enum = when(parser, Enum, "foo")

    # THEN the enum should contain the given comment
    assert enum.comment == "this is an enum"

    # THEN the enum item should contain the given comment
    assert enum.items[0].comment == "with comments"
