from typing import cast
from unittest.mock import Mock

import pytest
from more_itertools import one

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import (
    CollectionType,
    Enum,
    Flags,
    Function,
    GenericType,
    Interface,
    Primitive,
    Record,
    Type,
    TypeReference,
)
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.processing.processors.type_reference_checks import TypeReferenceChecks
from pydjinni.parser.providers.type_registry import TypeRegistry
from pydjinni.position import Position


@pytest.fixture
def type_reference_checks(type_registry_mock: Mock) -> TypeReferenceChecks:
    return TypeReferenceChecks(cast("TypeRegistry", type_registry_mock))


def test_unknown_type(type_registry_mock: Mock, type_reference_checks: TypeReferenceChecks):
    reference_position = Mock(Position)
    # GIVEN a type reference to an unknown type
    reference = TypeReference(
        position=reference_position,
        name=Identifier("foo"),
        parameters=(),
    )

    type_registry_mock.resolve.side_effect = TypeRegistry.TypeResolvingException(reference=reference)

    # WHEN executing the checks against the reference
    parse_result = type_reference_checks.process(reference)

    # THEN a ParseIssue reporting the unknown type should be returned
    assert one(parse_result.diagnostics) == Diagnostic(
        position=reference_position,
        description="Unknown type 'foo'",
        severity=Diagnostic.Severity.error,
    )


@pytest.mark.parametrize(
    "generic_type,rendering",
    (
        (
            CollectionType(
                name=Identifier("dict"),
                params=("K", "V"),
            ),
            "dict<K, V>",
        ),
        (
            CollectionType(
                name=Identifier("list"),
                params=("T",),
            ),
            "list<T>",
        ),
        (
            Interface(
                name=Identifier("foo"),
                params=("A", "B", "C"),
            ),
            "foo<A, B, C>",
        ),
    ),
)
def test_missing_generic_parameters(
    type_registry_mock: Mock,
    type_reference_checks: TypeReferenceChecks,
    generic_type: GenericType,
    rendering: str,
):
    reference_position = Mock(Position)
    # GIVEN a type reference with missing generic parameters
    reference = TypeReference(
        position=reference_position,
        name=Identifier("foo"),
        parameters=(),
    )

    type_registry_mock.resolve.return_value = generic_type

    # WHEN executing the checks against the reference
    parse_result = type_reference_checks.process(reference)

    # THEN a ParseIssue reporting the missing generic parameters should be returned
    assert one(parse_result.diagnostics) == Diagnostic(
        position=reference_position,
        description=f"Missing generic parameters for '{rendering}'.",
        severity=Diagnostic.Severity.error,
    )


@pytest.mark.parametrize(
    "generic_parameters_n, generic_type, error_message",
    (
        (
            1,
            CollectionType(
                name=Identifier("dict"),
                params=("K", "V"),
            ),
            "Invalid number of generic parameters given to 'dict<K, V>'. Expects 2, but 1 were given.",
        ),
        (
            3,
            CollectionType(
                name=Identifier("set"),
                params=("T",),
            ),
            "Invalid number of generic parameters given to 'set<T>'. Expects 1, but 3 were given.",
        ),
        (
            1,
            Interface(
                name=Identifier("foo"),
                params=("A", "B", "C"),
            ),
            "Invalid number of generic parameters given to 'foo<A, B, C>'. Expects 3, but 1 were given.",
        ),
    ),
)
def test_invalid_number_of_generic_parameters(
    type_registry_mock: Mock,
    type_reference_checks: TypeReferenceChecks,
    generic_parameters_n: int,
    generic_type: GenericType,
    error_message: str,
):
    reference_position = Mock(Position)
    # GIVEN a type reference with the wrong number of generic parameters
    reference = TypeReference(
        position=reference_position,
        name=Identifier("foo"),
        parameters=(Mock(TypeReference),) * generic_parameters_n,
    )

    type_registry_mock.resolve.return_value = generic_type

    # WHEN executing the checks against the reference
    parse_result = type_reference_checks.process(reference)

    # THEN a ParseIssue reporting the missing generic parameters should be returned
    assert one(parse_result.diagnostics) == Diagnostic(
        position=reference_position,
        description=error_message,
        severity=Diagnostic.Severity.error,
    )


@pytest.mark.parametrize(
    "non_generic_type",
    (
        Interface(
            name=Identifier("foo"),
        ),
        Mock(Primitive),
        Mock(Enum),
        Mock(Flags),
        Mock(Function),
        Mock(Record),
    ),
)
def test_not_accepting_generic_parameters(
    type_registry_mock: Mock,
    type_reference_checks: TypeReferenceChecks,
    non_generic_type: Type,
):
    reference_position = Mock(Position)
    # GIVEN a type reference with generic parameters on a non generic type
    reference = TypeReference(
        position=reference_position,
        name=Identifier("foo"),
        parameters=(Mock(TypeReference),),
    )

    type_registry_mock.resolve.return_value = non_generic_type

    # WHEN executing the checks against the reference
    parse_result = type_reference_checks.process(reference)

    # THEN a ParseIssue reporting the unallowed generic parameters should be returned
    assert one(parse_result.diagnostics) == Diagnostic(
        position=reference_position,
        description="Type 'foo' does not accept generic parameters",
        severity=Diagnostic.Severity.error,
    )
