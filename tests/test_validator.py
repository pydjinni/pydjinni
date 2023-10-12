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
