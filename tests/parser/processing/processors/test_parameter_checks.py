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
    Parameter,
    Primitive,
    Record,
    TypeReference,
)
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.processing.processors.parameter_checks import ParameterChecks
from pydjinni.position import Position
lazy from pydjinni.parser.providers.type_registry import TypeRegistry


@pytest.fixture
def parameter_checks(type_registry_mock: Mock) -> ParameterChecks:
    # GIVEN a ParameterChecks instance
    return ParameterChecks(cast("TypeRegistry", type_registry_mock))


def test_invalid_parameter_type(type_registry_mock: Mock, parameter_checks: ParameterChecks):
    reference_position = Mock(Position)
    # GIVEN a parameter with an ErrorType
    parameter = Parameter(
        name=Identifier("foo"),
        reference=TypeReference(
            position=reference_position,
            name=Identifier("bar"),
            parameters=(),
        ),
    )

    type_registry_mock.resolve.return_value = Mock(ErrorDomain)

    # WHEN executing the checks against the parameter
    parse_result = parameter_checks.process(parameter)

    # THEN a ParseIssue should be returned because an ErrorDomain cannot be passed as a parameter
    assert one(parse_result.diagnostics) == Diagnostic(
        position=reference_position,
        description="Cannot pass an error type as a parameter",
        severity=Diagnostic.Severity.error,
    )


@pytest.mark.parametrize(
    "field_type",
    (Record, Primitive, CollectionType, Interface, Function, Enum, Flags, None),
)
def test_unknown_or_valid_parameter_type(
    type_registry_mock: Mock, parameter_checks: ParameterChecks, field_type: type | None
):
    reference_position = Mock(Position)
    # GIVEN a parameter with a valid or unknown type
    parameter = Parameter(
        name=Identifier("foo"),
        reference=TypeReference(
            position=reference_position,
            name=Identifier("bar"),
            parameters=(),
        ),
    )

    type_registry_mock.resolve.return_value = field_type

    # WHEN executing the checks against the parameter
    parse_result = parameter_checks.process(parameter)

    # THEN a no ParseIssue should be returned
    assert len(parse_result.diagnostics) == 0
