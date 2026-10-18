# Copyright 2023 - 2026 jothepro
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

from typing import Final

import pytest
from dirty_equals import IsDict
from pydantic import TypeAdapter, ValidationError

from pydjinni.config.types import IdentifierStyle
from pydjinni.parser.model.identifier import Identifier


@pytest.fixture
def identifier_type_adapter() -> TypeAdapter[Identifier]:
    return TypeAdapter(Identifier)


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


@pytest.mark.parametrize("name,case,output", testdata)
def test_identifier_conversion(name: str, case: IdentifierStyle.Case, output: str):
    # GIVEN an Identifier instance
    identifier = Identifier(name)

    # WHEN converting the name with the given style
    converted = identifier.convert(case)

    # THEN the converted name should be as expected
    assert converted == output


@pytest.mark.parametrize("name,case,output", testdata)
def test_identifier_conversion_prefix(name: str, case: IdentifierStyle.Case, output: str):
    # GIVEN an Identifier instance
    identifier = Identifier(value=name)
    prefix = "m_"

    # WHEN converting the name with the given style and the defined prefix
    converted = identifier.convert(IdentifierStyle(style=case, prefix=prefix))

    # THEN the converted name should be prefixed
    assert converted == f"{prefix}{output}"


def test_identifier_pydantic_validation_serialization_and_schema(identifier_type_adapter: TypeAdapter[Identifier]):
    identifier: Final = identifier_type_adapter.validate_strings("some_name")
    assert isinstance(identifier, Identifier)
    assert identifier.value == "some_name"
    validation_schema = identifier_type_adapter.json_schema()
    assert validation_schema == IsDict(
        pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
        type="string",
    )


@pytest.mark.parametrize("input", ("&", "foo&", "_foo_bar", "1and2", "", "*test", "foo-bar"))
def test_identifier_invalid_pydantic_validation(identifier_type_adapter: TypeAdapter[Identifier], input: str):
    # GIVEN an invalid input
    # WHEN validating the input
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        identifier_type_adapter.validate_python(input)
