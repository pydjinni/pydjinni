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

import pytest
from pydantic import BaseModel, computed_field, Field

from pydjinni.generator.validator import LanguageKeywords, validate, InvalidIdentifierException
from pydjinni.parser.base_models import BaseType
from pydjinni.position import Position, Cursor


def test_validator():
    # GIVEN a list of keywords
    keywords = LanguageKeywords("Foo", ["bar", "baz"])

    # AND GIVEN a semantic model that applies validation on a field
    class Foo(BaseModel):
        decl: BaseType = Field(exclude=True, repr=False)

        @computed_field
        @validate(keywords)
        def bar(self):
            return "bar"

    foo = Foo(
        decl=BaseType(
            name="foo",
            position=Position(
                start=Cursor(line=0, col=2),
                end=Cursor(line=0, col=3),
                file=Path("foo/bar.baz")
            )
        )
    )

    # WHEN reading the computed property
    # THEN an InvalidIdentifierException should be raised
    with pytest.raises(InvalidIdentifierException, match="The identifier 'bar' is a reserved keyword in Foo"):
        baz = foo.bar
