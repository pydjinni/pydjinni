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

import sys
from textwrap import dedent

import pytest
import pytest_lsp
from lsprotocol.types import *
from pytest_lsp import (
    ClientServerConfig,
    LanguageClient,
    client_capabilities,
)


def when_did_open(client: LanguageClient, text: str):
    test_uri = "file:///path/to/interface.pydjinni"
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
    return test_uri


@pytest_lsp.fixture(
    config=ClientServerConfig(
        server_command=[sys.executable, "-m", "pydjinni_language_server", "start", "--connection", "STDIO", "--log", "pygls.log"],
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
async def test_did_open(client: LanguageClient):
    # WHEN opening a document
    test_uri = when_did_open(client, dedent("""
    # @deprecated
    foo = record { a: i8; }
    bar = record { b: foo }
    """))

    # THEN diagnostics should be published
    await client.wait_for_notification(TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)
    assert test_uri in client.diagnostics
    assert len(client.diagnostics[test_uri]) == 2

    parsing_error = client.diagnostics[test_uri][0]
    assert parsing_error.message.startswith("IDL Parsing error: missing ';' at '}'")
    assert parsing_error.severity == DiagnosticSeverity.Error

    deprecated_warning = client.diagnostics[test_uri][1]
    assert deprecated_warning.message.startswith("deprecated")
    assert deprecated_warning.severity == DiagnosticSeverity.Warning

    # AND WHEN requesting hover information for the `i8` type
    hover_result = await client.text_document_hover_async(HoverParams(
        text_document=TextDocumentIdentifier(test_uri),
        position=Position(line=2, character=19)
    ))

    # THEN the hover should give context for the type
    assert hover_result.range == Range(start=Position(line=2, character=18), end=Position(line=2, character=20))
    assert "8 bit integer type" in hover_result.contents.value

    # AND WHEN requesting the definition of the type `foo`
    definition_result = await client.text_document_definition_async(DefinitionParams(
        text_document=TextDocumentIdentifier(test_uri),
        position=Position(line=3, character=19)
    ))

    # THEN the position of the `foo` type definition should be returned
    assert definition_result.uri == test_uri
    assert definition_result.range == Range(start=Position(line=1, character=0), end=Position(line=2, character=23))

    # AND WHEN requesting hover information for the `foo` type reference
    hover_result = await client.text_document_hover_async(HoverParams(
        text_document=TextDocumentIdentifier(test_uri),
        position=Position(line=3, character=19)
    ))

    # THEN the hover should contain the deprecation warning
    assert "Deprecated" in hover_result.contents.value

    # AND WHEN requesting hover information for the `foo` type definition
    hover_result = await client.text_document_hover_async(HoverParams(
        text_document=TextDocumentIdentifier(test_uri),
        position=Position(line=2, character=1)
    ))

    # THEN the hover should contain the deprecation warning
    assert hover_result.range == Range(start=Position(line=2, character=0), end=Position(line=2, character=3))
    assert "Deprecated" in hover_result.contents.value

