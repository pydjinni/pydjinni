# Copyright 2025 - 2026 jothepro
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
from textwrap import dedent

import pytest
from dirty_equals import HasAttributes, IsInstance, IsList
from marko.block import BlankLine, Paragraph
from marko.inline import LineBreak, RawText

from pydjinni.parser.comment.comment_parser import CommentParser
from pydjinni.parser.comment.plugins import (
    DeprecatedCommand,
    InlineReference,
    ParamCommand,
    ReturnsCommand,
    ThrowsCommand,
)


@pytest.fixture
def parser():
    return CommentParser()


def test_markdown_plugins(parser: CommentParser):
    # WHEN parsing the markdown input containing special commands
    result = parser.parse(
        dedent(
            """
            hello world ``.type_reference``
            @param foo bar
            @param bar baz

            @deprecated
            @deprecated use instead: ``new``

            @returns foo
            @throws foo.baz bar
            hello world
            """,
        )
    )

    assert result.children == IsList(
        IsInstance(BlankLine),
        IsInstance(Paragraph)
        & HasAttributes(
            children=IsList(
                IsInstance(RawText) & HasAttributes(children="hello world "),
                IsInstance(InlineReference) & HasAttributes(children=".type_reference"),
                length=2,
            ),
        ),
        IsInstance(ParamCommand)
        & HasAttributes(
            parameter="foo",
            children=IsList(
                IsInstance(RawText) & HasAttributes(children="bar"),
                length=1,
            ),
        ),
        IsInstance(ParamCommand) & HasAttributes(parameter="bar"),
        IsInstance(BlankLine),
        IsInstance(DeprecatedCommand) & HasAttributes(children=IsList(length=0)),
        IsInstance(DeprecatedCommand)
        & HasAttributes(
            children=IsList(
                IsInstance(RawText) & HasAttributes(children="use instead: "),
                IsInstance(InlineReference) & HasAttributes(children="new"),
                length=2,
            ),
        ),
        IsInstance(BlankLine),
        IsInstance(ReturnsCommand)
        & HasAttributes(
            children=IsList(
                IsInstance(RawText) & HasAttributes(children="foo"),
                length=1,
            ),
        ),
        IsInstance(ThrowsCommand)
        & HasAttributes(
            parameter="foo.baz",
            children=IsList(
                IsInstance(RawText) & HasAttributes(children="bar"),
                IsInstance(LineBreak),
                IsInstance(RawText) & HasAttributes(children="hello world"),
                length=3,
            ),
        ),
        length=10,
    )


def test_empty_input(parser: CommentParser):
    # WHEN parsing an empty string
    result = parser.parse("")

    # THEN the result should be empty
    assert result.children == IsList(length=0)


def test_plain_text_without_commands(parser: CommentParser):
    # WHEN parsing a plain text string without commands
    result = parser.parse("This is plain text without commands.")

    # THEN the result should have one paragraph token
    assert result.children == IsList(IsInstance(Paragraph), length=1)
