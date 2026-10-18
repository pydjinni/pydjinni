from pathlib import Path
from textwrap import dedent
from unittest.mock import Mock

from dirty_equals import HasAttributes, IsInstance, IsList
from marko.block import BlankLine, Document, Paragraph
from marko.inline import LineBreak, RawText
from more_itertools import one
from pydantic import BaseModel

from pydjinni.parser.model.elements import Comment, CommentLine, TypeReference
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.model.namespace_tuple import NamespaceTuple
from pydjinni.position import Cursor, Position


class CommentContainer(BaseModel):
    comment: Comment


def test_comment_pydantic_validation_and_serialization():
    comment = "first line\nsecond line"
    parsed_comment = Comment.from_text(comment)
    assert parsed_comment.raw == comment

    from_comment = CommentContainer(comment=parsed_comment)
    assert from_comment.comment is parsed_comment
    assert from_comment.model_dump(mode="json") == {"comment": comment}
    assert from_comment.model_dump_json() == '{"comment":"first line\\nsecond line"}'

    from_dict = CommentContainer.model_validate({"comment": comment})
    assert isinstance(from_dict.comment, Comment)
    assert from_dict.comment.raw == comment

    from_json = CommentContainer.model_validate_json("""{"comment": "first line\\nsecond line"}""")
    assert isinstance(from_json.comment, Comment)
    assert from_json.comment.raw == comment

    assert CommentContainer.model_json_schema()["properties"]["comment"]["type"] == "string"
    assert CommentContainer.model_json_schema(mode="serialization")["properties"]["comment"]["type"] == "string"


def test_comment_deprecated_description():
    comment = Comment.from_text(
        dedent(
            """
            this is some comment

            @deprecated because it is old
            second line
            """,
        )
    )
    assert isinstance(comment.deprecated, Document)
    children = comment.deprecated.children
    assert children == IsList(
        IsInstance(RawText) & HasAttributes(children="because it is old"),
        IsInstance(LineBreak),
        IsInstance(RawText) & HasAttributes(children="second line"),
        length=3,
    )


def test_comment_deprecated():
    comment = Comment.from_text(
        dedent(
            """
            this is some comment
            @deprecated
            """,
        )
    )
    assert isinstance(comment.deprecated, bool)
    assert comment.deprecated


def test_comment_not_deprecated():
    comment = Comment.from_text(
        dedent(
            """
            this is some comment
            """,
        )
    )
    assert isinstance(comment.deprecated, bool)
    assert not comment.deprecated


def test_comment_parameters():
    comment = Comment.from_text(
        dedent(
            """
            this is some comment
            @param foo
            @param bar is the second parameter
            """,
        )
    )
    assert len(comment.parameters) == 2
    assert comment.parameters["foo"].children == IsList(length=0)
    bar_param = comment.parameters["bar"]
    assert bar_param.children == IsList(
        IsInstance(RawText) & HasAttributes(children="is the second parameter"),
        length=1,
    )


def test_comment_throws():
    comment = Comment.from_text(
        dedent(
            """
            @throws foo
            
            this is some comment
            @throws bar if something else is wrong
            """,
        )
    )
    assert len(comment.throws) == 2
    assert comment.throws["foo"].children == IsList(length=0)
    bar_throws = comment.throws["bar"]
    assert bar_throws.children == IsList(
        IsInstance(RawText) & HasAttributes(children="if something else is wrong"),
        length=1,
    )


def test_comment_returns():
    comment = Comment.from_text(
        dedent(
            """
            @returns the answer to the life, the universe, and everything
            """,
        )
    )
    assert comment.returns is not None
    content = comment.returns.children
    assert content == IsList(
        IsInstance(RawText) & HasAttributes(children="the answer to the life, the universe, and everything"),
        length=1,
    )


def test_comment_without_commands():
    comment = Comment.from_text(
        dedent(
            """
            some comment with a few commands
            @throws when nobody is looking

            @returns some information
            """,
        )
    )
    without_commands = comment.without_commands
    assert without_commands.children == IsList(
        IsInstance(BlankLine),
        IsInstance(Paragraph),
        IsInstance(BlankLine),
        length=3,
    )


def test_comment_inline_reference():
    path = Mock(Path)
    element = CommentLine(
        position=Position(
            file=path,
            start=Cursor(line=1, col=0),
            end=Cursor(line=1, col=36),
        ),
        content=" some comment with a ``foo.bar.reference``!",
    )
    assert one(element.children) == TypeReference(
        position=Position(
            file=path,
            start=Cursor(line=1, col=23),
            end=Cursor(line=1, col=40),
        ),
        name=Identifier(
            value="reference",
            position=Position(
                file=path,
                start=Cursor(line=1, col=31),
                end=Cursor(line=1, col=40),
            ),
        ),
        namespace_prefix=NamespaceTuple(
            (
                Identifier(
                    value="foo",
                    position=Position(
                        file=path,
                        start=Cursor(line=1, col=23),
                        end=Cursor(line=1, col=26),
                    ),
                ),
                Identifier(
                    value="bar",
                    position=Position(
                        file=path,
                        start=Cursor(line=1, col=27),
                        end=Cursor(line=1, col=30),
                    ),
                ),
            ),
        ),
        parameters=(),
        required_resolution=False,
    )


def test_absolute_comment_inline_reference():
    path = Mock(Path)
    element = CommentLine(
        position=Position(
            file=path,
            start=Cursor(line=1, col=0),
            end=Cursor(line=1, col=36),
        ),
        content=" some ``.foo.reference`` is absolute",
    )
    assert one(element.children) == TypeReference(
        position=Position(
            file=path,
            start=Cursor(line=1, col=8),
            end=Cursor(line=1, col=22),
        ),
        name=Identifier(
            value="reference",
            position=Position(
                file=path,
                start=Cursor(line=1, col=13),
                end=Cursor(line=1, col=22),
            ),
        ),
        namespace_prefix=NamespaceTuple(
            (
                Identifier(
                    value="foo",
                    position=Position(
                        file=path,
                        start=Cursor(line=1, col=9),
                        end=Cursor(line=1, col=12),
                    ),
                ),
            ),
        ),
        absolute=True,
        parameters=(),
        required_resolution=False,
    )


def test_comment_throws_reference():
    path = Mock(Path)
    namespace = NamespaceTuple((Identifier("foo"),))
    element = CommentLine(
        position=Position(
            file=path,
            start=Cursor(line=2, col=1),
            end=Cursor(line=2, col=50),
        ),
        namespace=namespace,
        content=" @throws foo if something goes wrong",
    )
    assert one(element.children) == TypeReference(
        position=Position(
            file=path,
            start=Cursor(line=2, col=10),
            end=Cursor(line=2, col=13),
        ),
        namespace=namespace,
        name=Identifier(
            value="foo",
            position=Position(
                file=path,
                start=Cursor(line=2, col=10),
                end=Cursor(line=2, col=13),
            ),
        ),
        parameters=(),
        required_resolution=False,
    )


def test_absolute_comment_throws_reference():
    path = Mock(Path)
    namespace = NamespaceTuple((Identifier("foo"),))
    element = CommentLine(
        position=Position(
            file=path,
            start=Cursor(line=2, col=1),
            end=Cursor(line=2, col=50),
        ),
        namespace=namespace,
        content=" @throws .foo.bar if something goes wrong",
    )
    assert one(element.children) == TypeReference(
        position=Position(
            file=path,
            start=Cursor(line=2, col=10),
            end=Cursor(line=2, col=18),
        ),
        namespace=namespace,
        name=Identifier(
            value="bar",
            position=Position(
                file=path,
                start=Cursor(line=2, col=15),
                end=Cursor(line=2, col=18),
            ),
        ),
        namespace_prefix=NamespaceTuple(
            (
                Identifier(
                    value="foo",
                    position=Position(
                        file=path,
                        start=Cursor(line=2, col=11),
                        end=Cursor(line=2, col=14),
                    ),
                ),
            ),
        ),
        absolute=True,
        parameters=(),
        required_resolution=False,
    )
