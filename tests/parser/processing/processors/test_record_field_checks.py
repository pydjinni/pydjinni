from typing import cast
from unittest.mock import Mock

import pytest
from more_itertools import one

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import (
    CollectionType,
    Enum,
    ErrorDomain,
    Flags,
    Function,
    Interface,
    Primitive,
    Record,
    TypeReference,
)
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.processing.processors.record_field_checks import RecordFieldChecks
from pydjinni.position import Position
lazy from pydjinni.parser.providers.type_registry import TypeRegistry


@pytest.fixture
def record_field_checks(type_registry_mock: Mock) -> RecordFieldChecks:
    return RecordFieldChecks(cast("TypeRegistry", type_registry_mock))


@pytest.mark.parametrize(
    "field_type,parse_issue_message",
    (
        (ErrorDomain, "Cannot assign an error as record field type"),
        (Interface, "Cannot assign an interface as record field type"),
        (Function, "Cannot assign a function as record field type"),
    ),
)
def test_invalid_record_field_type(
    type_registry_mock: Mock,
    record_field_checks: RecordFieldChecks,
    field_type: type,
    parse_issue_message: str,
):
    type_reference_position = Mock(Position)
    # GIVEN a Record.Field with an invalid type
    field = Record.Field(
        name=Identifier("foo"),
        reference=TypeReference(
            position=type_reference_position,
            name=Identifier("bar"),
            parameters=(),
        ),
    )

    type_registry_mock.resolve.return_value = Mock(field_type)

    # WHEN executing the checks against the field
    parse_result = record_field_checks.process(field)

    # THEN a ParseIssue should be returned because the provided type cannot be used as a record field type
    assert one(parse_result.diagnostics) == Diagnostic(
        position=field.reference.position,
        description=parse_issue_message,
        severity=Diagnostic.Severity.error,
    )


@pytest.mark.parametrize(
    "field_type",
    (Record, Primitive, CollectionType, Enum, Flags, None),
)
def test_unknown_or_valid_field_type(
    type_registry_mock: Mock,
    record_field_checks: RecordFieldChecks,
    field_type: type | None,
):
    type_reference_position = Mock(Position)
    # GIVEN a Record.Field with an unknown or valid type
    field = Record.Field(
        name=Identifier("foo"),
        reference=TypeReference(
            position=type_reference_position,
            name=Identifier("bar"),
            parameters=(),
        ),
    )

    type_registry_mock.resolve.return_value = field_type

    # WHEN executing the checks against the field
    parse_result = record_field_checks.process(field)

    # THEN a no ParseIssue should be returned
    assert len(parse_result.diagnostics) == 0
