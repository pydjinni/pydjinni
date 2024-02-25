import json
import os
import traceback
import uuid
from pathlib import Path, WindowsPath, PosixPath
from urllib.parse import unquote

import click
import logging

from lsprotocol import types as lsp
from lsprotocol.types import RelativePattern, MessageType

from pydjinni import API
from pydjinni.defs import DEFAULT_CONFIG_PATH
from pydjinni.exceptions import ApplicationException, ConfigurationException
from pygls.server import LanguageServer
from pygls.workspace import TextDocument
from importlib.metadata import version

from pydjinni.parser.base_models import TypeReference, BaseType
from pydjinni.parser.parser import Parser

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11

logger = logging.getLogger(__name__)


def main():
    cli()


class ConnectionType(StrEnum):
    TCP = "TCP"
    STDIO = "STDIO"


class TextDocumentPath(WindowsPath if os.name == 'nt' else PosixPath):
    def __new__(cls, document: TextDocument):
        self = super().__new__(cls, document.uri)
        self.document = document
        return self

    def read_text(self, encoding=None, errors=None):
        return self.document.source

    def as_uri(self):
        return self.document.uri


def error_logger(func):
    def inner_function(ls, *args, **kwargs):
        try:
            return func(ls, *args, **kwargs)
        except Exception as e:
            ls.show_message_log(traceback.format_exc(), msg_type=MessageType.Error)
    return inner_function

@click.group()
@click.version_option(package_name="pydjinni")
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
              type=click.Choice(ConnectionType, case_sensitive=False),
              default=ConnectionType.TCP,
              help="Connection type of the language server.")
@click.option('--host', '-h', type=str, default='127.0.0.1', help="Hostname for the TCP server.")
@click.option('--port', '-p', type=int, default=8080, help="Port for the TCP server.")
@click.option('--config', '-c', default=DEFAULT_CONFIG_PATH, type=Path, help="Path to the PyDjinni configuration file.")
@click.option('--log', '-l', default=None, type=Path, help="Log file for the Language Server.")
def start(connection, host: str, port: int, config: Path, log: Path = None):
    """
    Start a Language Server
    """
    server = LanguageServer("pydjinni-language-server", version('pydjinni'))
    if log:
        logging.basicConfig(filename=log, filemode='w', level=logging.DEBUG)

    hover_cache: dict[str, dict[int, dict[int, TypeReference]]] = {}
    dependency_cache: dict[str, set[str]] = {}

    def to_diagnostic(error: ApplicationException):
        return lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(error.position.start.line - 1, error.position.start.col),
                end=lsp.Position(error.position.end.line - 1, error.position.end.col)
            ),
            message=f"{error.__doc__}: {error.description}",
            source=type(server).__name__
        )

    def to_hover_cache(type_refs: list[TypeReference]) -> dict[int, dict[int, TypeReference]]:
        cache: dict[int, dict[int, TypeReference]] = {}

        def cache_ref(ref: TypeReference):
            for i in range(ref.position.start.col, ref.position.end.col):
                cache[ref.position.start.line][i] = ref
            for parameter_ref in ref.parameters:
                cache_ref(parameter_ref)

        for ref in type_refs:
            if not cache.get(ref.position.start.line):
                cache[ref.position.start.line] = {}

            cache_ref(ref)
        return cache

    def validate(ls, uri):
        ls.show_message_log(f"Validating {unquote(uri)}")
        document: TextDocument = ls.workspace.get_text_document(uri)
        error_items = []
        refs = []
        path = TextDocumentPath(document)
        try:
            if config.exists():
                api = API().configure(path=config)
            else:
                api = API().configure(options={
                    "generate": {}
                })
            refs = api.parse(path).refs
        except Parser.ParsingExceptionList as e:
            error_items = [to_diagnostic(error) for error in e.items
                           if isinstance(error.position.file, TextDocumentPath)
                           and error.position.file.document.uri == uri]
            refs = e.type_refs
        except ConfigurationException as e:
            ls.show_message_log(str(e), lsp.MessageType.Error)
            ls.show_message(f"PyDjinni: {e}", lsp.MessageType.Error)

        ls.publish_diagnostics(document.uri, error_items)

        hover_cache[uri] = to_hover_cache(
            [ref for ref in refs
             if isinstance(ref.position.file, TextDocumentPath)
             and ref.position.file.document.uri == uri]
        )

        dependency_cache[uri] = set([ref.type_def.position.file.as_uri() for ref in refs if
                                     ref.type_def
                                     and isinstance(ref.type_def, BaseType)
                                     and ref.type_def.position.file and ref.type_def.position.file.as_uri() != uri]
                                    + [config.absolute().as_uri()])

    @server.feature(lsp.INITIALIZED)
    @error_logger
    def init(ls, _):
        ls.show_message_log(f"Initialized PyDjinni language server {version('pydjinni')}")
        for workspace_folder in server.workspace.folders.values():
            ls.register_capability(lsp.RegistrationParams(
                registrations=[
                    lsp.Registration(
                        id=str(uuid.uuid4()),
                        method=lsp.WORKSPACE_DID_CHANGE_WATCHED_FILES,
                        register_options=lsp.DidChangeWatchedFilesRegistrationOptions(watchers=[
                            lsp.FileSystemWatcher(
                                glob_pattern=RelativePattern(workspace_folder, "**/*.{pydjinni,djinni}"),
                                kind=lsp.WatchKind.Create | lsp.WatchKind.Change | lsp.WatchKind.Delete
                            )
                        ])
                    )
                ]
            ))

            if not config.exists():
                config_uri = config.absolute().as_uri()
                ls.show_message_log(f"{config_uri} cannot be found!", lsp.MessageType.Warning)
                ls.show_message(f"PyDjinni: Configuration file cannot be found:\n{config_uri}", lsp.MessageType.Warning)
            ls.register_capability(lsp.RegistrationParams(
                registrations=[
                    lsp.Registration(
                        id=str(uuid.uuid4()),
                        method=lsp.WORKSPACE_DID_CHANGE_WATCHED_FILES,
                        register_options=lsp.DidChangeWatchedFilesRegistrationOptions(watchers=[
                            lsp.FileSystemWatcher(
                                glob_pattern=RelativePattern(workspace_folder, config.as_posix()),
                                kind=lsp.WatchKind.Create | lsp.WatchKind.Change | lsp.WatchKind.Delete
                            )
                        ])
                    )
                ]
            ))

    @server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
    @error_logger
    def did_change(ls, params: lsp.DidChangeTextDocumentParams):
        ls.show_message_log(f"Did Change: {unquote(params.text_document.uri)}")
        validate(ls, params.text_document.uri)

    @server.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
    @error_logger
    def did_close(ls: LanguageServer, params: lsp.DidCloseTextDocumentParams):
        path = unquote(params.text_document.uri)
        ls.show_message_log(f"Did Close: {path}")
        hover_cache.pop(params.text_document.uri, {})
        dependency_cache.pop(params.text_document.uri, {})
        for cache in dependency_cache.values():
            if path in cache:
                cache.remove(path)

    @server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
    @error_logger
    def did_open(ls, params: lsp.DidOpenTextDocumentParams):
        ls.show_message_log(f"Did Open: {unquote(params.text_document.uri)}")
        validate(ls, params.text_document.uri)

    @server.feature(lsp.TEXT_DOCUMENT_HOVER)
    @error_logger
    def hover(ls, params: lsp.HoverParams):
        row = params.position.line + 1
        col = params.position.character
        uri = params.text_document.uri
        ls.show_message_log(f"Hover request in {unquote(uri)}: {row}, {col}")

        cache_entry: TypeReference | None = hover_cache[uri].get(row, {}).get(col, None)
        if cache_entry and cache_entry.type_def and cache_entry.type_def.comment:
            return lsp.Hover(
                contents=lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown,
                    value=cache_entry.type_def.comment
                ),
                range=lsp.Range(
                    start=lsp.Position(cache_entry.position.start.line - 1, cache_entry.position.start.col),
                    end=lsp.Position(cache_entry.position.end.line - 1, cache_entry.position.end.col)
                )
            )

    @server.feature(lsp.TEXT_DOCUMENT_DEFINITION)
    @error_logger
    def definition(ls, params: lsp.DefinitionParams):
        row = params.position.line + 1
        col = params.position.character
        ls.show_message_log(f"Go To Definition request: {row}, {col}")
        cache_entry: TypeReference | None = hover_cache[params.text_document.uri].get(row, {}).get(col, None)
        if cache_entry and cache_entry.type_def and isinstance(cache_entry.type_def,
                                                               BaseType) and cache_entry.type_def.position.file:
            return lsp.Location(
                uri=cache_entry.type_def.position.file.as_uri(),
                range=lsp.Range(
                    start=lsp.Position(cache_entry.type_def.position.start.line - 1,
                                       cache_entry.type_def.position.start.col),
                    end=lsp.Position(cache_entry.type_def.position.end.line - 1, cache_entry.type_def.position.end.col)
                )
            )

    @server.feature(lsp.WORKSPACE_DID_CHANGE_WATCHED_FILES)
    @error_logger
    def did_change_watched_files(ls, params: lsp.DidChangeWatchedFilesParams):
        for change in params.changes:
            path = unquote(change.uri)
            ls.show_message_log(f"Did Change: {path}")
            ls.show_message_log(f"Searching for dependents that need updating...")
            for uri, dependencies in dependency_cache.items():
                if path in dependencies:
                    validate(ls, uri)

    match connection:
        case ConnectionType.TCP:
            server.start_tcp(host, port)
        case ConnectionType.STDIO:
            server.start_io()
