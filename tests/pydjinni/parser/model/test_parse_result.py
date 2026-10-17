from unittest.mock import MagicMock, Mock

from more_itertools import one
from pytest_unordered import unordered

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import Enum, Interface, Namespace, Record
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.position import Position


def test_ast_reported_errors():
    # GIVEN an ParseResult instance with multiple issues
    error = Diagnostic(
        position=Mock(Position),
        description="",
        severity=Diagnostic.Severity.error,
    )

    ast = ParseResult(
        elements=(),
        diagnostics=(
            error,
            Diagnostic(
                position=Mock(Position),
                description="",
                severity=Diagnostic.Severity.warning,
            ),
            Diagnostic(
                position=Mock(Position),
                description="",
                severity=Diagnostic.Severity.info,
            ),
        ),
    )

    # WHEN calling the `errors` property
    errors = ast.errors

    # THEN only ParseIssues with severity ERROR should be returned
    assert one(errors) == error


def test_ast_filtering():
    # GIVEN an ParseResult instance with different elements
    first_interface = MagicMock(Interface)
    second_interface = MagicMock(Interface)
    ast = ParseResult(
        elements=(
            first_interface,
            Namespace(
                name=Identifier("foo"),
                types=(second_interface,),
                namespaces=(),
            ),
            MagicMock(Record),
            MagicMock(Enum),
        ),
        diagnostics=(),
    )

    # WHEN filtering for only Interface elements
    filtered_elements = ast.filter_elements(Interface)

    # THEN a flat list with only the filtered elements should be returned
    assert filtered_elements == unordered(first_interface, second_interface)


def test_ast_union_filtering():
    # GIVEN an ParseResult instance with different elements
    interface = MagicMock(Interface)
    record = MagicMock(Record)
    ast = ParseResult(
        elements=(
            interface,
            Namespace(
                name=Identifier("foo"),
                types=(record,),
                namespaces=(),
            ),
            MagicMock(Enum),
        ),
        diagnostics=(),
    )

    # WHEN filtering for multiple different types
    filtered_elements = ast.filter_elements(Interface, Record)

    # THEN a flat list of only the filtered elemets should be returned
    assert filtered_elements == unordered(interface, record)


def test_append():
    # GIVEN an ParseResult instance
    first_element = MagicMock(Interface)
    first_diagnostic = Mock(Diagnostic)
    first_ast = ParseResult(
        elements=(first_element,),
        diagnostics=(first_diagnostic,),
    )

    # AND GIVEN a second ParseResult instance
    second_element = MagicMock(Record)
    second_diagnostic = Mock(Diagnostic)
    second_ast = ParseResult(
        elements=(second_element,),
        diagnostics=(second_diagnostic,),
    )

    # WHEN appending the second to the first ParseResult
    resulting_ast = first_ast.append(second_ast)

    # THEN an ast containing all items from both ParseResults should be returned
    assert resulting_ast.elements == (first_element, second_element)
    assert resulting_ast.diagnostics == (first_diagnostic, second_diagnostic)


def test_from_parse_issue():
    # GIVEN a parse_issue
    diagnostic_mock = MagicMock(Diagnostic)

    # WHEN creating an ParseResult from just the issue
    ast = ParseResult.from_parse_diagnostics(diagnostic_mock)

    # THEN an ParseResult containing just the issue should be returned
    assert one(ast.diagnostics) == diagnostic_mock
    assert len(ast.elements) == 0
