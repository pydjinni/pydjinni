import sys

import pytest
import pytest_lsp
from lsprotocol.types import (
    InitializeParams,
    DidOpenTextDocumentParams,
    TextDocumentItem,
    TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS,
)
from pytest_lsp import (
    ClientServerConfig,
    LanguageClient,
    client_capabilities,
)


@pytest_lsp.fixture(
    config=ClientServerConfig(
        server_command=[sys.executable, "-m", "pydjinni_language_server", "start", "--connection", "STDIO"],
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
async def test_did_open_diagnostics(client: LanguageClient):
    test_uri = "file:///path/to/interface.pydjinni"
    client.text_document_did_open(
        DidOpenTextDocumentParams(
            text_document=TextDocumentItem(
                uri=test_uri,
                language_id="pydjinni",
                version=1,
                text="foo = record { a: i8; }",
            )
        )
    )

    # Wait for the server to publish its diagnostics
    await client.wait_for_notification(TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)

    assert test_uri in client.diagnostics
    assert len(client.diagnostics[test_uri]) == 0


@pytest.mark.asyncio
async def test_did_open_diagnostics_error(client: LanguageClient):
    test_uri = "file:///path/to/interface.pydjinni"
    client.text_document_did_open(
        DidOpenTextDocumentParams(
            text_document=TextDocumentItem(
                uri=test_uri,
                language_id="pydjinni",
                version=1,
                text="foo = record { a: i8 }",
            )
        )
    )

    # Wait for the server to publish its diagnostics
    await client.wait_for_notification(TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)

    assert test_uri in client.diagnostics
    assert len(client.diagnostics[test_uri]) == 1
    assert client.diagnostics[test_uri][0].message.startswith("IDL Parsing error: missing ';' at '}'")
