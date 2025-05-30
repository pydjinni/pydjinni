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
from textwrap import dedent

from pydjinni.parser.base_models import TypeReference, CommentTypeReference
from pydjinni.parser.markdown_parser import MarkdownParser
from pydjinni.position import Position, Cursor


def test_markdown_plugins():
    # GIVEN a Markdown parser instance
    type_references: list[TypeReference] = []
    parser = MarkdownParser(type_references)

    # WHEN parsing the markdown input containing special commands
    tokens, state = parser.parse(
        dedent(
            """
            hello world ``type_reference``
            @param foo bar
            @param bar baz

            @deprecated
            @deprecated because of something

            @returns foo
            @throws baz bar
            hello world
            """
        ),
        position=Position(start=Cursor(line=0, col=0), end=Cursor(line=8, col=11), file=Path("test.pydjinni")),
        namespace=[],
    )

    assert len(tokens) == 10

    # THEN the special commands should be parsed correctly
    assert tokens[1]["children"][1]["attrs"]["type_ref"] == CommentTypeReference(
        name="type_reference",
        namespace=[],
        position=Position(start=Cursor(line=0, col=16), end=Cursor(line=0, col=30), file=Path("test.pydjinni")),
        identifier_position=Position(
            start=Cursor(line=0, col=16), end=Cursor(line=0, col=30), file=Path("test.pydjinni")
        ),
    )
    assert tokens[2]["type"] == "param"
    assert tokens[2]["attrs"]["name"] == "foo"
    assert tokens[2]["children"][0]["raw"] == "bar"
    assert tokens[3]["type"] == "param"
    assert tokens[3]["attrs"]["name"] == "bar"
    assert tokens[3]["children"][0]["raw"] == "baz"
    assert tokens[5]["type"] == "deprecated"
    assert tokens[5]["children"][0]["raw"] == ""
    assert tokens[6]["type"] == "deprecated"
    assert tokens[6]["children"][0]["raw"] == "because of something"
    assert tokens[8]["type"] == "returns"
    assert tokens[8]["children"][0]["raw"] == "foo"
    assert tokens[9]["type"] == "throws"
    assert tokens[9]["attrs"]["type_ref"] == CommentTypeReference(
        name="baz",
        namespace=[],
        position=Position(start=Cursor(line=9, col=9), end=Cursor(line=9, col=12), file=Path("test.pydjinni")),
        identifier_position=Position(
            start=Cursor(line=9, col=9), end=Cursor(line=9, col=12), file=Path("test.pydjinni")
        ),
    )
    assert tokens[9]["children"][0]["raw"] == "bar"

    # THEN the @throws type reference should be added to the type_references list
    assert len(type_references) == 2
    assert type_references[0].name == "baz"
    assert type_references[1].name == "type_reference"
