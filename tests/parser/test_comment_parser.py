from pathlib import Path

from pydjinni.parser.base_models import TypeReference, CommentTypeReference
from pydjinni.parser.markdown_parser import MarkdownParser
from pydjinni.position import Position, Cursor


def test_markdown_plugins():
    # GIVEN a Markdown parser instance
    type_references: list[TypeReference] = []
    parser = MarkdownParser(type_references)

    # WHEN parsing the markdown input containing special commands
    tokens, state = parser.parse("""hello world
@param foo bar
@param bar baz

@deprecated
@deprecated because of something

@returns foo
@throws baz bar
hello world""", position=Position(start=Cursor(line=0, col=0), end=Cursor(line=8, col=11), file=Path("test.pydjinni")), namespace=[])

    # THEN the special commands should be parsed correctly
    assert tokens[1]['type'] == "param"
    assert tokens[1]['attrs']['name'] == "foo"
    assert tokens[1]['children'][0]['raw'] == "bar"
    assert tokens[2]['type'] == "param"
    assert tokens[2]['attrs']['name'] == "bar"
    assert tokens[2]['children'][0]['raw'] == "baz"
    assert tokens[4]['type'] == "deprecated"
    assert tokens[4]['children'][0]['raw'] == ""
    assert tokens[5]['type'] == "deprecated"
    assert tokens[5]['children'][0]['raw'] == "because of something"
    assert tokens[7]['type'] == "returns"
    assert tokens[7]['children'][0]['raw'] == "foo"
    assert tokens[8]['type'] == "throws"
    assert tokens[8]['attrs']['type_ref'] == CommentTypeReference(
        name="baz",
        namespace=[],
        position=Position(start=Cursor(line=8, col=9), end=Cursor(line=8, col=12), file=Path("test.pydjinni")),
    )
    assert tokens[8]['children'][0]['raw'] == "bar"

    # THEN the @throws type reference should be added to the type_references list
    assert len(type_references) == 1
    assert type_references[0].name == "baz"
