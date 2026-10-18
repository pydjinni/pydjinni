from typing import Final

from dirty_equals import IsDict, IsPartialDict
from pydantic import TypeAdapter

from pydjinni.config.model.identifier_style import IdentifierStyle, IdentifierStyleLike


def test_bare_case_exposes_style_and_empty_prefix():
    style: Final = TypeAdapter(IdentifierStyleLike).validate_python("snake_case")

    assert isinstance(style, IdentifierStyle.Case)
    assert style.style == IdentifierStyle.Case.snake
    assert style.prefix == ""


def test_identifier_style_exposes_style_and_prefix():
    style: Final = TypeAdapter(IdentifierStyleLike).validate_python({
        "style": "camelCase",
        "prefix": "m_",
    })

    assert isinstance(style, IdentifierStyle)
    assert style.style == IdentifierStyle.Case.camel
    assert style.prefix == "m_"


def test_identifier_style_schema():
    schema: Final = TypeAdapter(IdentifierStyleLike).json_schema()

    assert schema["$defs"]["IdentifierStyle"] == IsPartialDict(
        properties=IsDict(
            style={"$ref": "#/$defs/Case"},
            prefix=IsPartialDict(type="string", default=""),
        ),
        required=["style"],
    )
    assert schema["$defs"]["Case"] == IsPartialDict(
        type="string",
        enum=[case.value for case in IdentifierStyle.Case],
    )
    assert schema["anyOf"] == [
        {"$ref": "#/$defs/IdentifierStyle"},
        {"$ref": "#/$defs/Case"},
    ]
