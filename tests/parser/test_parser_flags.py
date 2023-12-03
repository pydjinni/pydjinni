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

from pydjinni.parser.ast import Flags
from test_parser import given, when


def assert_flag(flag: Flags.Flag, name: str, none: bool = False, all: bool = False):
    """asserts that a flag has all attributes set as excepted"""
    assert flag.name == name
    assert flag.none == none
    assert flag.all == all


def test_parsing_flags(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = flags {
            flag1;
            flag2;
            no_flags = none;
            all_flags = all;
        }
        """
    )

    flags = when(parser, Flags, "foo")

    flag_items = flags.flags

    # THEN the resulting flags should have exactly 4 items
    assert len(flag_items) == 4
    assert_flag(flag_items[0], name="flag1")
    assert_flag(flag_items[1], name="flag2")
    assert_flag(flag_items[2], name="no_flags", none=True)
    assert_flag(flag_items[3], name="all_flags", all=True)


def test_parsing_flags_comment(tmp_path: Path):
    # given flags with comments
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            # this is a flag
            foo = flags {
                # with comments
                flag1;
            }
            """
    )

    # WHEN parsing the input
    flags = when(parser, Flags, "foo")

    # THEN the flags type should contain the given comment
    assert flags.comment == " this is a flag"

    # THEN the flag should contain the given comment
    assert flags.flags[0].comment == " with comments"
