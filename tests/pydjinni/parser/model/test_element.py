import pytest
from pydantic import ValidationError

from pydjinni.parser.model.elements import Interface, Record
from pydjinni.parser.model.identifier import Identifier


def test_element_immutability():
    # GIVEN an Element subclass instance
    element = Record(name=Identifier("bar"))

    # WHEN trying to assign a new value to an object property
    # THEN a ValidationError should be raised because Elements are immutable
    with pytest.raises(ValidationError):
        element.name = Identifier("new_name")


def test_element_no_extra_fields():
    # WHEN trying to initialize an Element subclass with extra (unknown) arguments
    # THEN a ValidationError shoud be raised
    with pytest.raises(ValidationError):
        Interface(
            name=Identifier("foo"),
            unknown="bar",  # pyright: ignore[reportCallIssue]
        )
