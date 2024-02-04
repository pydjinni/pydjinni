import json
import os
from pathlib import Path, WindowsPath, PosixPath

import click
import logging

from lsprotocol import types as lsp

from pydjinni import API
from pydjinni.defs import DEFAULT_CONFIG_PATH
from pydjinni.exceptions import ApplicationException
from pygls.server import LanguageServer
from pygls.workspace import TextDocument
from importlib.metadata import version

from pydjinni.exceptions import ApplicationExceptionList

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11

logger = logging.getLogger(__name__)


def main():
    try:
        cli()
    except ApplicationException as e:
        logger.error(e)
        exit(e.code)
    except ApplicationExceptionList as e:
        for item in e.items:
            logger.error(item)
        exit(e.items[0].code)


class ConnectionType(StrEnum):
    TCP = "TCP"
    STDIO = "STDIO"
    WEBSOCKET = "WEBSOCKET"


class TextDocumentPath(WindowsPath if os.name == 'nt' else PosixPath):
    def __new__(cls, document: TextDocument):
        self = super().__new__(cls, document.uri)
        self.document = document
        return self

    def read_text(self, encoding=None, errors=None):
        return self.document.source


@click.group()
@click.version_option()
def cli():
    """PyDjinni Language Server Utilities"""
    pass


@cli.command()
def config_schema():
    """
    Print the configuration file JSON-Schema
    """
    print(json.dumps(API().configuration_model.model_json_schema(), indent=4))

@cli.command()
@click.option('--connection',
              type=click.Choice([connection for connection in ConnectionType], case_sensitive=False),
              default=ConnectionType.TCP,
              help="Connection type of the language server")
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8080)
@click.option('--config', '-c', default=DEFAULT_CONFIG_PATH, type=Path, help="path to the config file.")
def start(connection, host, port, config):
    """
    Start a Language Server
    """
    server = LanguageServer("pydjinni-language-server", version('pydjinni'))

    parser = API().configure(config)

    def to_diagnostic(error: ApplicationException):
        return lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(error.position.start.line - 1, error.position.start.col),
                end=lsp.Position(error.position.end.line - 1, error.position.end.col)
            ),
            message=f"{error.__doc__}: {error.description}",
            source=type(server).__name__
        )

    def validate(ls, params):
        ls.show_message_log("Validating pydjinni IDL...")

        document: TextDocument = ls.workspace.get_text_document(params.text_document.uri)

        error_items = []
        try:
            path = TextDocumentPath(document)
            parser.parse(path)
        except ApplicationException as e:
            error_items = [to_diagnostic(e)]
        except ApplicationExceptionList as e:
            error_items = [to_diagnostic(error) for error in e.items]

        ls.publish_diagnostics(document.uri, error_items)

    @server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls, params: lsp.DidChangeTextDocumentParams):
        """Text document did change notification."""
        server.show_message_log("Text Document Did Change")
        validate(ls, params)

    @server.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
    def did_close(server: LanguageServer, params: lsp.DidCloseTextDocumentParams):
        """Text document did close notification."""
        server.show_message_log("Text Document Did Close")

    @server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls, params: lsp.DidOpenTextDocumentParams):
        """Text document did open notification."""
        ls.show_message_log(f"Text Document Did Open: {params.text_document.language_id}")
        validate(ls, params)

    match connection:
        case ConnectionType.TCP:
            server.start_tcp(host, port)
        case ConnectionType.STDIO:
            server.start_io()
        case ConnectionType.WEBSOCKET:
            server.start_ws(host, port)
