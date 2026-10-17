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

import pytest
from pydantic import BaseModel

from pydjinni.config.types import IdentifierStyle
from pydjinni.parser.model.identifier import Identifier

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


def test_identifier_pydantic_validation_serialization_and_schema():
    class IdentifierContainer(BaseModel):
        identifier: Identifier

    identifier = IdentifierContainer.model_validate({"identifier": "some_name"})

    assert isinstance(identifier.identifier, Identifier)
    assert identifier.model_dump(mode="json") == {"identifier": "some_name"}
    assert identifier.model_dump_json() == '{"identifier":"some_name"}'
    validation_schema = IdentifierContainer.model_json_schema()
    serialization_schema = IdentifierContainer.model_json_schema(mode="serialization")
    assert validation_schema["properties"]["identifier"]["pattern"] == r"[_\w]+"
    assert validation_schema["properties"]["identifier"]["type"] == "string"
    assert serialization_schema["properties"]["identifier"]["pattern"] == r"[_\w]+"
    assert serialization_schema["properties"]["identifier"]["type"] == "string"
