from textwrap import dedent
lazy from pathlib import Path

import pytest
from pytest_unordered import unordered

from pydjinni.exceptions import FileNotFoundException, InputParsingException
from pydjinni.parser.model.elements import (
    CollectionType,
    Enum,
    ErrorDomain,
    Flags,
    Function,
    Interface,
    Primitive,
    Record,
)
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.yaml.yaml_type_parser import YamlTypeParser
from pydjinni.position import Cursor, Position

AnyParseType = Record | Interface | Enum | Flags | Function | CollectionType | ErrorDomain | Primitive


@pytest.fixture
def file(tmp_path: Path):
    return tmp_path / "input.yaml"


@pytest.mark.parametrize(
    "kind,expected_type",
    [
        ("record", Record),
        ("interface", Interface),
        ("enum", Enum),
        ("flags", Flags),
        ("function", Function),
        ("collection", CollectionType),
        ("primitive", Primitive),
        ("error", ErrorDomain),
    ],
)
def test_deserialize_types(file: Path, kind: str, expected_type: type):
    """Test deserialization of all supported PyDjinni types."""
    file.write_text(
        dedent(f"""
            kind: {kind}
            name: test_type
            """)
    )
    deserialized_type = next(YamlTypeParser(AnyParseType).parse(file))

    assert isinstance(deserialized_type, expected_type)
    assert deserialized_type.name == Identifier("test_type")
    assert deserialized_type.position == Position(
        file=file,
        start=Cursor(line=1, col=0),
        end=Cursor(line=3, col=0),
    )


def test_missing_file(file: Path):
    # GIVEN a file that does not exist
    # WHEN attempting to deserialize it
    # THEN a FileNotFoundException should be raised
    with pytest.raises(FileNotFoundException):
        next(YamlTypeParser(AnyParseType).parse(file))


@pytest.mark.parametrize(
    "input",
    [":", "foo", "---", "foo:bar", "%YAML 9.9\n---\nkind: record\nname: test_record"],
)
def test_invalid_input(file: Path, input: str):
    # GIVEN a file that does not contain invalid or unexpected YAML input
    file.write_text(input)

    # WHEN attempting to deserialize it
    # THEN an InputParsingException should be raised
    with pytest.raises(InputParsingException):
        next(YamlTypeParser(AnyParseType).parse(file))


@pytest.mark.parametrize(
    "input",
    [
        "",
        " ",
    ],
)
def test_empty_input(file: Path, input: str):
    file.write_text(input)
    # GIVEN an empty file
    # WHEN attempting to deserialize it
    # THEN an no output should be produced
    with pytest.raises(StopIteration):
        next(YamlTypeParser(AnyParseType).parse(file))


def test_invalid_data(file: Path):
    # GIVEN a valid YAML file that cannot be deserialized
    file.write_text("foo: bar")

    # WHEN attempting to deserialize it
    # THEN an InputParsingException should be raised
    with pytest.raises(InputParsingException):
        next(YamlTypeParser(AnyParseType).parse(file))


def test_multi_document_input(file: Path):
    # GIVEN a valid multi-document YAML
    file.write_text(
        dedent("""
            ---
            kind: record
            name: test_record
            ---
            kind: interface
            name: test_interface
            """)
    )

    # WHEN deserializing it
    deserialized_types = [deserialized_type for deserialized_type in YamlTypeParser(AnyParseType).parse(file)]

    # THEN all types should be returned
    assert deserialized_types == unordered(
        Record(
            position=Position(file=file, start=Cursor(line=2, col=0), end=Cursor(line=4, col=0)),
            name=Identifier("test_record"),
        ),
        Interface(
            position=Position(file=file, start=Cursor(line=5, col=0), end=Cursor(line=7, col=0)),
            name=Identifier("test_interface"),
        ),
    )
