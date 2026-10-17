from typing import cast
from unittest.mock import Mock

import pytest
from more_itertools import one

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import Enum, Flags, Interface
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.processors.type_registration import TypeRegistration
from pydjinni.parser.providers.type_registry import TypeRegistry
from pydjinni.position import Position


@pytest.fixture
def type_registration(type_registry_mock: Mock) -> TypeRegistration:
    return TypeRegistration(cast("TypeRegistry", type_registry_mock))


def test_successful_type_registration(type_registration: TypeRegistration):
    # WHEN processing any type
    parse_result = type_registration.process(Mock(Interface))

    # THEN an empty ParseResult should be returned
    assert parse_result == ParseResult((), ())


def test_duplicate_type_error(type_registry_mock: Mock, type_registration: TypeRegistration):
    # GIVEN a TypeRegistry that raises a DuplicateTypeException when trying to register
    existing_type_position = Mock(Position)
    new_type_position = Mock(Position)
    new_type = Flags(
        position=new_type_position,
        name=Identifier("foo"),
    )
    type_registry_mock.register.side_effect = TypeRegistry.DuplicateTypeException(
        new_type=new_type,
        existing_type=Enum(
            position=existing_type_position,
            name=Identifier("bar"),
        ),
    )

    # WHEN processing a type_reference
    parse_result = type_registration.process(new_type)

    # THEN TypeRegistration.register should be called with the new element
    type_registry_mock.register.assert_called_once_with(new_type)

    # THEN a duplicate typ should be reported
    assert one(parse_result.diagnostics) == Diagnostic(
        position=new_type_position,
        description="Duplicate type detected",
        severity=Diagnostic.Severity.error,
        related_information=(
            Diagnostic.RelatedInformation(
                position=existing_type_position,
                description="Previous type definition is here.",
            ),
        ),
    )
