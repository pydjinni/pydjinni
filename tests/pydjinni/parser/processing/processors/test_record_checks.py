from unittest.mock import Mock

from more_itertools import one

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import CollectionType, Record, TypeReference
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.processing.processors.record_checks import RecordChecks
from pydjinni.parser.providers.type_registry import TypeRegistry
from pydjinni.position import Position


def test_ord_deriving_collections():
    field_position = Mock(Position)
    # GIVEN a record that is both deriving 'ord' and has a field of type collection
    record = Record(
        name=Identifier("foo"),
        fields=(
            Record.Field(
                position=field_position,
                name=Identifier("bar"),
                reference=TypeReference(
                    name=Identifier("baz"),
                    parameters=(),
                ),
            ),
        ),
        deriving=frozenset({Record.Deriving.ord}),
    )

    registry_mock = Mock(TypeRegistry)
    registry_mock.resolve.return_value = Mock(CollectionType)

    # AND GIVEN a RecordChecks instance
    checks = RecordChecks(registry_mock)

    # WHEN executing the checks against the record
    parse_result = checks.process(record)

    # THEN a ParseIssue should be returned because records deriving 'ord' cannot contain collections
    assert one(parse_result.diagnostics) == Diagnostic(
        position=field_position,
        description="Cannot compare collections in 'ord' deriving",
        severity=Diagnostic.Severity.error,
    )
