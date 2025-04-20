# Copyright 2025 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from pathlib import Path
import sys
from textwrap import dedent
from typing import cast

import pytest
import pytest_lsp
from lsprotocol.types import *
from pytest_lsp import ClientServerConfig, LanguageClient, client_capabilities

test_uri = "file:///path/to/interface.pydjinni"


async def when_did_open(client: LanguageClient, text: str):
    client.text_document_did_open(
        DidOpenTextDocumentParams(
            text_document=TextDocumentItem(uri=test_uri, language_id="pydjinni", version=1, text=text)
        )
    )
    await client.wait_for_notification(TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)


async def assert_hover(client: LanguageClient, position: Position, expected_range: Range, expected_contents: list[str]):
    # WHEN requesting hover information
    hover_result = await client.text_document_hover_async(
        HoverParams(
            text_document=TextDocumentIdentifier(test_uri),
            position=position,
        )
    )

    # THEN the hover should give context for the type
    assert hover_result
    assert hover_result.range == expected_range
    for expected_content in expected_contents:
        assert expected_content in cast(MarkupContent, hover_result.contents).value


async def assert_definition(
    client: LanguageClient, position: Position, expected_range: Range, expected_uri: str = test_uri
):
    # WHEN requesting a type definition
    definition_result = cast(
        Location,
        await client.text_document_definition_async(
            DefinitionParams(text_document=TextDocumentIdentifier(test_uri), position=position)
        ),
    )

    # THEN the position of the `foo` type definition should be returned
    assert definition_result.range == expected_range
    assert definition_result.uri == expected_uri


@dataclass
class DiagnosticExpectation:
    severity: DiagnosticSeverity
    range: Range
    contents: list[str]


async def assert_diagnostics(client: LanguageClient, expected_diagnostics: list[DiagnosticExpectation]):
    assert test_uri in client.diagnostics
    assert len(client.diagnostics[test_uri]) == len(expected_diagnostics)
    for diagnostic, expected in zip(client.diagnostics[test_uri], expected_diagnostics):
        assert diagnostic.severity == expected.severity
        assert diagnostic.range == expected.range
        for expected_content in expected.contents:
            assert expected_content in diagnostic.message


@dataclass
class DocumentSymbolExpectation:
    name: str
    kind: SymbolKind
    range: Range
    deprecated: bool = False
    children: list["DocumentSymbolExpectation"] | None = None


async def assert_document_symbols(client: LanguageClient, expected_symbols: list[DocumentSymbolExpectation]):
    document_symbols = cast(
        list[DocumentSymbol],
        await client.text_document_document_symbol_async(
            DocumentSymbolParams(text_document=TextDocumentIdentifier(test_uri))
        ),
    )
    assert document_symbols

    def assert_symbol_expectation(symbols: list[DocumentSymbol], expectations: list[DocumentSymbolExpectation]):
        for symbol, expectation in zip(symbols, expectations):
            assert symbol.name == expectation.name
            assert symbol.kind == expectation.kind
            assert symbol.range == expectation.range
            if expectation.deprecated:
                assert symbol.deprecated
            if symbol.children:
                assert expectation.children
                assert_symbol_expectation(symbol.children, expectation.children)

    assert_symbol_expectation(document_symbols, expected_symbols)


@dataclass
class CodeLensExpectation:
    range: Range
    title: str
    command: str
    arguments: list[Any] | None = None


async def assert_code_lenses(client: LanguageClient, expected_code_lenses: list[CodeLensExpectation]):
    code_lenses = cast(
        list[CodeLens],
        await client.text_document_code_lens_async(CodeLensParams(text_document=TextDocumentIdentifier(test_uri))),
    )
    assert len(code_lenses) == len(expected_code_lenses)
    for lens, expectation in zip(code_lenses, expected_code_lenses):
        assert lens.range.start == expectation.range.start
        assert lens.command
        assert lens.command.title == expectation.title
        assert lens.command.command == expectation.command
        if expectation.arguments:
            assert lens.command.arguments == expectation.arguments


@pytest_lsp.fixture(
    config=ClientServerConfig(
        server_command=[
            sys.executable,
            "-m",
            "pydjinni_language_server",
            "start",
            "--connection",
            "STDIO",
            "--log",
            "pygls.log",
        ]
    )
)
async def client(lsp_client: LanguageClient, tmp_path: Path):
    # Setup
    await lsp_client.initialize_session(
        InitializeParams(
            capabilities=client_capabilities("visual-studio-code"), root_uri=tmp_path.as_uri(), root_path=str(tmp_path)
        )
    )

    yield

    # Teardown
    await lsp_client.shutdown_session()


@pytest.mark.asyncio
async def test_code_lenses(client: LanguageClient, tmp_path: Path):
    (tmp_path / "pydjinni.yaml").write_text(
        dedent(
            """
            generate:
                cpp:
                    out: out/cpp
                    namespace: test
            """
        )
    )
    (tmp_path / "out" / "cpp").mkdir(parents=True)
    (tmp_path / "out" / "cpp" / "foo.hpp").write_text(
        dedent(
            """
            #pragma once
            """
        )
    )
    # WHEN opening a document with a record
    await when_did_open(
        client,
        dedent(
            """
            # some record
            foo = record { a: i8; }
            """
        ),
    )

    # THEN no code lenses should be available
    await assert_code_lenses(
        client,
        [
            CodeLensExpectation(
                range=Range(start=Position(line=2, character=0), end=Position(line=2, character=3)),
                title="C++",
                command="open_generated_interface",
                arguments=[(tmp_path / "out" / "cpp" / "foo.hpp").as_uri()],
            )
        ],
    )
