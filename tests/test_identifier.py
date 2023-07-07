import pytest

from pydjinni.config.types import IdentifierStyle
from pydjinni.parser.identifier import IdentifierType as Identifier

testdata = [
    ("foo_bar", IdentifierStyle.Case.none, "foo_bar"),
    ("foobar", IdentifierStyle.Case.none, "foobar"),
    ("Foo_Bar", IdentifierStyle.Case.none, "Foo_Bar"),
    ("FooBar", IdentifierStyle.Case.none, "FooBar"),
    ("foo_bar", IdentifierStyle.Case.camel, "fooBar"),
    ("foobar", IdentifierStyle.Case.camel, "foobar"),
    ("Foo_Bar", IdentifierStyle.Case.camel, "fooBar"),
    ("FooBar", IdentifierStyle.Case.camel, "foobar"),
    ("foo_bar", IdentifierStyle.Case.pascal, "FooBar"),
    ("foobar", IdentifierStyle.Case.pascal, "Foobar"),
    ("Foo_Bar", IdentifierStyle.Case.pascal, "FooBar"),
    ("FooBar", IdentifierStyle.Case.pascal, "Foobar"),
    ("foo_bar", IdentifierStyle.Case.snake, "foo_bar"),
    ("foobar", IdentifierStyle.Case.snake, "foobar"),
    ("Foo_Bar", IdentifierStyle.Case.snake, "foo_bar"),
    ("FooBar", IdentifierStyle.Case.snake, "foobar"),
    ("foo_bar", IdentifierStyle.Case.kebab, "foo-bar"),
    ("foobar", IdentifierStyle.Case.kebab, "foobar"),
    ("Foo_Bar", IdentifierStyle.Case.kebab, "foo-bar"),
    ("FooBar", IdentifierStyle.Case.kebab, "foobar"),
    ("foo_bar", IdentifierStyle.Case.train, "FOO_BAR"),
    ("foobar", IdentifierStyle.Case.train, "FOOBAR"),
    ("Foo_Bar", IdentifierStyle.Case.train, "FOO_BAR"),
    ("FooBar", IdentifierStyle.Case.train, "FOOBAR"),
]


@pytest.mark.parametrize("name,style,output", testdata)
def test_identifier_conversion(name, style, output):
    # GIVEN an Identifier instance
    identifier = Identifier(name)

    # WHEN converting the name with the given style
    converted = identifier.convert(style)

    # THEN the converted name should be as expected
    assert converted == output


@pytest.mark.parametrize("name,style,output", testdata)
def test_identifier_conversion_prefix(name, style, output):
    # GIVEN an Identifier instance
    identifier = Identifier(name)
    prefix = "m_"

    # WHEN converting the name with the given style and the defined prefix
    converted = identifier.convert(IdentifierStyle(style=style, prefix=prefix))

    # THEN the converted name should be prefixed
    assert converted == f"{prefix}{output}"
