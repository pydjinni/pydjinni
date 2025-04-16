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
import sys
from textwrap import dedent
from typing import cast

import pytest
import pytest_lsp
from lsprotocol.types import *
from pytest_lsp import (
    ClientServerConfig,
    LanguageClient,
    client_capabilities,
)

test_uri = "file:///path/to/interface.pydjinni"


async def when_did_open(client: LanguageClient, text: str):
    client.text_document_did_open(
        DidOpenTextDocumentParams(
            text_document=TextDocumentItem(
                uri=test_uri,
                language_id="pydjinni",
                version=1,
                text=text,
            )
        )
    )
    await client.wait_for_notification(TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)


async def assert_hover(client: LanguageClient, position: Position, expected_range: Range, expected_contents: list[str]):
    # WHEN requesting hover information
    hover_result = await client.text_document_hover_async(
        HoverParams(text_document=TextDocumentIdentifier(test_uri), position=position)
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
            DefinitionParams(
                text_document=TextDocumentIdentifier(test_uri),
                position=position,
            )
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
    for index, diagnostic in enumerate(client.diagnostics[test_uri]):
        assert diagnostic.severity == expected_diagnostics[index].severity
        assert diagnostic.range == expected_diagnostics[index].range
        for expected_content in expected_diagnostics[index].contents:
            assert expected_content in diagnostic.message


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
        ],
    ),
)
async def client(lsp_client: LanguageClient):
    # Setup
    response = await lsp_client.initialize_session(
        InitializeParams(
            capabilities=client_capabilities("visual-studio-code"),
            root_uri="file:///path/to/test/project/root/",
        )
    )

    yield

    # Teardown
    await lsp_client.shutdown_session()


@pytest.mark.asyncio
async def test_record(client: LanguageClient):
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


@pytest.mark.asyncio
async def test_interface(client: LanguageClient):
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
            ),
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
