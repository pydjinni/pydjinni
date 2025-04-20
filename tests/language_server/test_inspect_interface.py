from textwrap import dedent
import pytest
from pytest_lsp import LanguageClient
from lsprotocol.types import *
from test_language_server import (
    DiagnosticExpectation,
    DocumentSymbolExpectation,
    assert_code_lenses,
    assert_diagnostics,
    assert_document_symbols,
    assert_hover,
    when_did_open,
    client
)


@pytest.mark.asyncio
async def test_inspect_interface(client: LanguageClient):
    # WHEN opening a document with an interface
    await when_did_open(
        client,
        dedent(
            """
            # some **interesting** interface
            foo = main interface +cpp {
                static get_instance() -> foo;
                # @param param is a parameter
                # @returns returns an integer
                bar(param: bool) -> i32;
                # a method that is throwing
                # @throws some_error when something goes wrong
                throwing_method() throws some_error;
            }
            """
        ),
    )

    # THEN the expected diagnostics should be reported
    await assert_diagnostics(
        client,
        [
            DiagnosticExpectation(
                severity=DiagnosticSeverity.Error,
                range=Range(start=Position(line=9, character=29), end=Position(line=9, character=39)),
                contents=["Type resolving error: Unknown type 'some_error'"],
            )
        ],
    )

    # THEN the hover information should be correct
    await assert_hover(
        client,
        position=Position(line=2, character=1),
        expected_range=Range(start=Position(line=2, character=0), end=Position(line=2, character=3)),
        expected_contents=["some **interesting** interface"],
    )

    await assert_hover(
        client,
        position=Position(line=3, character=30),
        expected_range=Range(start=Position(line=3, character=29), end=Position(line=3, character=32)),
        expected_contents=["some **interesting** interface"],
    )

    await assert_hover(
        client,
        position=Position(line=6, character=6),
        expected_range=Range(start=Position(line=6, character=4), end=Position(line=6, character=7)),
        expected_contents=["Parameter", "`param` is a parameter", "Returns", "an integer"],
    )

    await assert_hover(
        client,
        position=Position(line=6, character=9),
        expected_range=Range(start=Position(line=6, character=8), end=Position(line=6, character=13)),
        expected_contents=["is a parameter"],
    )

    await assert_hover(
        client,
        position=Position(line=6, character=17),
        expected_range=Range(start=Position(line=6, character=15), end=Position(line=6, character=19)),
        expected_contents=["boolean type"],
    )

    await assert_hover(
        client,
        position=Position(line=6, character=25),
        expected_range=Range(start=Position(line=6, character=24), end=Position(line=6, character=27)),
        expected_contents=["32 bit integer type"],
    )

    await assert_hover(
        client,
        position=Position(line=9, character=5),
        expected_range=Range(start=Position(line=9, character=4), end=Position(line=9, character=19)),
        expected_contents=["a method that is throwing", "Throws", "`some_error` when something goes wrong"],
    )

    await assert_document_symbols(
        client,
        [
            DocumentSymbolExpectation(
                name="foo",
                kind=SymbolKind.Interface,
                range=Range(start=Position(line=1, character=0), end=Position(line=10, character=1)),
                children=[
                    DocumentSymbolExpectation(
                        name="get_instance",
                        kind=SymbolKind.Method,
                        range=Range(start=Position(line=3, character=4), end=Position(line=3, character=33)),
                    ),
                    DocumentSymbolExpectation(
                        name="bar",
                        kind=SymbolKind.Method,
                        range=Range(start=Position(line=4, character=4), end=Position(line=6, character=28)),
                        children=[
                            DocumentSymbolExpectation(
                                name="param",
                                kind=SymbolKind.Variable,
                                range=Range(start=Position(line=6, character=8), end=Position(line=6, character=19)),
                            ),
                        ],
                    ),
                    DocumentSymbolExpectation(
                        name="throwing_method",
                        kind=SymbolKind.Method,
                        range=Range(start=Position(line=7, character=4), end=Position(line=9, character=40)),
                    ),
                ],
            )
        ],
    )

    # THEN no code lenses should be available
    await assert_code_lenses(client, [])
