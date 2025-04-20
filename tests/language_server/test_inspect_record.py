from textwrap import dedent
import pytest
from pytest_lsp import LanguageClient
from lsprotocol.types import *
from test_language_server import (
    DiagnosticExpectation,
    DocumentSymbolExpectation,
    assert_code_lenses,
    assert_definition,
    assert_diagnostics,
    assert_document_symbols,
    assert_hover,
    when_did_open,
    client,
)


@pytest.mark.asyncio
async def test_inspect_record(client: LanguageClient):
    # WHEN opening a document with records
    await when_did_open(
        client,
        dedent(
            """
            # foo is a record
            # @deprecated because it is outdated
            foo = record { a: i8; }
            bar = record { b: foo }
            """
        ),
    )

    # THEN the expected diagnostics should be reported
    await assert_diagnostics(
        client,
        [
            DiagnosticExpectation(
                severity=DiagnosticSeverity.Error,
                range=Range(start=Position(line=4, character=22), end=Position(line=4, character=22)),
                contents=["IDL Parsing error: missing ';' at '}'"],
            ),
            DiagnosticExpectation(
                severity=DiagnosticSeverity.Warning,
                range=Range(start=Position(line=4, character=18), end=Position(line=4, character=21)),
                contents=["deprecated", "because it is outdated"],
            ),
        ],
    )

    # THEN the hover information should be correct
    await assert_hover(
        client,
        position=Position(line=3, character=19),
        expected_range=Range(start=Position(line=3, character=18), end=Position(line=3, character=20)),
        expected_contents=["8 bit integer type"],
    )
    await assert_hover(
        client,
        position=Position(line=3, character=1),
        expected_range=Range(start=Position(line=3, character=0), end=Position(line=3, character=3)),
        expected_contents=["foo is a record", "**Deprecated** because it is outdated"],
    )
    await assert_hover(
        client,
        position=Position(line=4, character=19),
        expected_range=Range(start=Position(line=4, character=18), end=Position(line=4, character=21)),
        expected_contents=["foo is a record", "**Deprecated** because it is outdated"],
    )

    # THEN the definition location should be correct
    await assert_definition(
        client,
        position=Position(line=4, character=19),
        expected_range=Range(start=Position(line=1, character=0), end=Position(line=3, character=23)),
    )

    # THEN the document symbols should be correct
    await assert_document_symbols(
        client,
        [
            DocumentSymbolExpectation(
                name="foo",
                kind=SymbolKind.Class,
                range=Range(start=Position(line=1, character=0), end=Position(line=3, character=23)),
                deprecated=True,
                children=[
                    DocumentSymbolExpectation(
                        name="a",
                        kind=SymbolKind.Field,
                        range=Range(start=Position(line=3, character=15), end=Position(line=3, character=21)),
                    )
                ],
            ),
            DocumentSymbolExpectation(
                name="bar",
                kind=SymbolKind.Class,
                range=Range(start=Position(line=4, character=0), end=Position(line=4, character=23)),
                children=[
                    DocumentSymbolExpectation(
                        name="b",
                        kind=SymbolKind.Field,
                        range=Range(start=Position(line=4, character=15), end=Position(line=4, character=21)),
                    )
                ],
            ),
        ],
    )

    # THEN no code lenses should be available
    await assert_code_lenses(client, [])
