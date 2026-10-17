from typing import cast
from unittest.mock import Mock

import pytest
from more_itertools import one
from pytest_unordered import unordered

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import ErrorDomain, Function, Interface, TypeReference
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.processing.processors.method_and_function_checks import MethodAndFunctionChecks
from pydjinni.position import Position
lazy from pydjinni.parser.providers.type_registry import TypeRegistry


@pytest.fixture
def method_and_function_checks(type_registry_mock: Mock) -> MethodAndFunctionChecks:
    # GIVEN a MethodAndFunctionChecks instance
    return MethodAndFunctionChecks(cast("TypeRegistry", type_registry_mock))


def test_invalid_return_type_method(
    type_registry_mock: Mock,
    method_and_function_checks: MethodAndFunctionChecks,
):
    return_type_reference_position = Mock(Position)
    # GIVEN an Interface.Method with an ErrorDomain as return type
    method = Interface.Method(
        name=Identifier("foo"),
        static=False,
        const=False,
        return_reference=TypeReference(
            position=return_type_reference_position,
            name=Identifier("bar"),
            parameters=(),
        ),
        asynchronous=False,
        parameters=(),
        throwing=(),
    )
    # AND GIVEN a TypeRegistry that returns an ErrorDomain type
    type_registry_mock.resolve.return_value = Mock(ErrorDomain)

    # WHEN executing the checks against the interface
    parse_result = method_and_function_checks.process(method)

    # THEN a parse issue should report that one cannot return error types
    assert one(parse_result.diagnostics) == Diagnostic(
        position=return_type_reference_position,
        description="Cannot return an error type",
        severity=Diagnostic.Severity.error,
    )


def test_invalid_return_type_function(
    type_registry_mock: Mock,
    method_and_function_checks: MethodAndFunctionChecks,
):
    return_type_reference_position = Mock(Position)
    # GIVEN a Function with an ErrorDomain as return type
    method = Function(
        name=Identifier("foo"),
        return_reference=TypeReference(
            position=return_type_reference_position,
            name=Identifier("bar"),
            parameters=(),
        ),
        parameters=(),
        throwing=(),
    )
    # AND GIVEN a TypeRegistry that returns an ErrorDomain type
    type_registry_mock.resolve.return_value = Mock(ErrorDomain)

    # WHEN executing the checks against the interface
    parse_result = method_and_function_checks.process(method)

    # THEN a parse issue should report that one cannot return error types
    assert one(parse_result.diagnostics) == Diagnostic(
        position=return_type_reference_position,
        description="Cannot return an error type",
        severity=Diagnostic.Severity.error,
    )


def test_invalid_throw_type_method(
    type_registry_mock: Mock,
    method_and_function_checks: MethodAndFunctionChecks,
):
    throw_type_reference_position = Mock(Position)
    # GIVEN an Interface.Method with a non ErrorDomain throw type
    method = Interface.Method(
        name=Identifier("foo"),
        static=False,
        const=False,
        return_reference=None,
        asynchronous=False,
        parameters=(),
        throwing=(
            TypeReference(
                position=throw_type_reference_position,
                name=Identifier("bar"),
                parameters=(),
            ),
        ),
    )
    # AND GIVEN a TypeRegistry that returns a type which is not an ErrorDomain
    type_registry_mock.resolve.return_value = Mock(Interface)

    # WHEN executing the checks against the interface
    parse_result = method_and_function_checks.process(method)

    # THEN a parse issue should report that one cannot throw non ErrorDomain types
    assert one(parse_result.diagnostics) == Diagnostic(
        position=throw_type_reference_position,
        description="Only errors can be thrown",
        severity=Diagnostic.Severity.error,
    )


def test_invalid_throw_type_function(
    type_registry_mock: Mock,
    method_and_function_checks: MethodAndFunctionChecks,
):
    throw_type_reference_position = Mock(Position)
    # GIVEN a Function with an non ErrorDomain throw type
    method = Function(
        name=Identifier("foo"),
        return_reference=None,
        parameters=(),
        throwing=(
            TypeReference(
                position=throw_type_reference_position,
                name=Identifier("bar"),
                parameters=(),
            ),
        ),
    )
    # AND GIVEN a TypeRegistry that returns a type which is not an ErrorDomain
    type_registry_mock.resolve.return_value = Mock(Interface)

    # WHEN executing the checks against the interface
    parse_result = method_and_function_checks.process(method)

    # THEN a parse issue should report that one cannot throw non ErrorDomain types
    assert one(parse_result.diagnostics) == Diagnostic(
        position=throw_type_reference_position,
        description="Only errors can be thrown",
        severity=Diagnostic.Severity.error,
    )


def test_invalid_throw_type_and_return_type_function(
    type_registry_mock: Mock,
    method_and_function_checks: MethodAndFunctionChecks,
):
    return_type_reference_position = Mock(Position)
    throw_type_reference_position = Mock(Position)
    # GIVEN a Function with an ErrorDomain as return type AND a non ErrorDomain throw type
    method = Function(
        name=Identifier("foo"),
        return_reference=TypeReference(
            position=return_type_reference_position,
            name=Identifier("error_type"),
            parameters=(),
        ),
        parameters=(),
        throwing=(
            TypeReference(
                position=throw_type_reference_position,
                name=Identifier("non_error_type"),
                parameters=(),
            ),
        ),
    )
    # AND GIVEN a TypeRegistry that resolves "error_type" to an ErrorDomain, and everything else to a non-ErrorDomain type
    type_registry_mock.resolve.side_effect = Mock(ErrorDomain), Mock(Interface)

    # WHEN executing the checks against the interface
    parse_result = method_and_function_checks.process(method)

    # THEN two parse issues should report that wrong type usage
    assert parse_result.diagnostics == unordered(
        Diagnostic(
            position=return_type_reference_position,
            description="Cannot return an error type",
            severity=Diagnostic.Severity.error,
        ),
        Diagnostic(
            position=throw_type_reference_position,
            description="Only errors can be thrown",
            severity=Diagnostic.Severity.error,
        ),
    )
