import json
import logging
import os
import uuid
from importlib.metadata import version
from pathlib import Path
from urllib.parse import unquote

import click
from lsprotocol.types import *
from pydjinni import API
from pydjinni.defs import DEFAULT_CONFIG_PATH
from pydjinni.exceptions import ApplicationException, ConfigurationException
from pydjinni.parser.base_models import TypeReference, BaseType
from pydjinni.parser.parser import Parser
from pydjinni_language_server.text_document_path import TextDocumentPath
from pygls.server import LanguageServer
from pygls.workspace import TextDocument

from .error_logger import error_logger
from .tolerant_converter import tolerant_converter

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
              default=ConnectionType.STDIO,
              help="Connection type of the language server.")
@click.option('--host', '-h', type=str, default='127.0.0.1', help="Hostname for the TCP server.")
@click.option('--port', '-p', type=int, default=8080, help="Port for the TCP server.")
@click.option('--config', '-c', default=DEFAULT_CONFIG_PATH, type=Path, help="Path to the PyDjinni configuration file.")
@click.option('--log', '-l', default=None, type=Path, help="Log file for the Language Server.")
def start(connection, host: str, port: int, config: Path, log: Path = None):
    """
    Start a Language Server
    """
    server = LanguageServer("pydjinni-language-server", version('pydjinni'), converter_factory=tolerant_converter)
    if log:
        logging.basicConfig(filename=log, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

    hover_cache: dict[str, dict[int, dict[int, TypeReference]]] = {}
    dependency_cache: dict[str, set[str]] = {}

    def to_diagnostic(error: ApplicationException):
        return Diagnostic(
            range=Range(
                start=Position(error.position.start.line - 1, error.position.start.col),
                end=Position(error.position.end.line - 1, error.position.end.col)
            ),
            severity=DiagnosticSeverity.Error,
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
            ls.show_message_log(str(e), MessageType.Error)
            ls.show_message(f"PyDjinni: {e}", MessageType.Error)

        for ref in refs:
            if (isinstance(ref.position.file, TextDocumentPath)
                    and ref.position.file.document.uri == uri
                    and ref.type_def and ref.type_def.deprecated):
                error_items.append(
                    Diagnostic(
                        range=Range(
                            start=Position(ref.position.start.line - 1, ref.position.start.col),
                            end=Position(ref.position.end.line - 1, ref.position.end.col)
                        ),
                        severity=DiagnosticSeverity.Warning,
                        message=f"deprecated: {ref.type_def.deprecated if isinstance(ref.type_def.deprecated, str) else ''}",
                        source=type(server).__name__
                    )
                )

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

    @server.feature(INITIALIZED)
    @error_logger
    def init(ls, _):
        ls.show_message_log(f"Initialized PyDjinni language server {version('pydjinni')}")
        ls.show_message_log(f"Working directory: {Path(os.getcwd()).absolute().as_uri()}")

        if not config.exists():
            config_uri = config.absolute().as_uri()
            ls.show_message_log(f"{config_uri} cannot be found!", MessageType.Warning)
            ls.show_message(f"PyDjinni: Configuration file cannot be found:\n{config_uri}", MessageType.Error)
        else:
            ls.show_message_log(f"Configuration file: {config.absolute().as_uri()}")
        if log:
            ls.show_message_log(f"Log files are written to: {log.absolute().as_uri()}")
        else:
            ls.show_message_log(f"Log files are disabled")
        for workspace_folder in server.workspace.folders.values():
            ls.register_capability(RegistrationParams(
                registrations=[
                    Registration(
                        id=str(uuid.uuid4()),
                        method=WORKSPACE_DID_CHANGE_WATCHED_FILES,
                        register_options=DidChangeWatchedFilesRegistrationOptions(watchers=[
                            FileSystemWatcher(
                                glob_pattern=RelativePattern(workspace_folder, "**/*.pydjinni"),
                                kind=WatchKind.Create | WatchKind.Change | WatchKind.Delete
                            )
                        ])
                    )
                ]
            ))
            ls.register_capability(RegistrationParams(
                registrations=[
                    Registration(
                        id=str(uuid.uuid4()),
                        method=WORKSPACE_DID_CHANGE_WATCHED_FILES,
                        register_options=DidChangeWatchedFilesRegistrationOptions(watchers=[
                            FileSystemWatcher(
                                glob_pattern=RelativePattern(workspace_folder, config.as_posix()),
                                kind=WatchKind.Create | WatchKind.Change | WatchKind.Delete
                            )
                        ])
                    )
                ]
            ))

    @server.feature(TEXT_DOCUMENT_DID_CHANGE)
    @error_logger
    def did_change(ls, params: DidChangeTextDocumentParams):
        ls.show_message_log(f"Did Change: {unquote(params.text_document.uri)}")
        validate(ls, params.text_document.uri)

    @server.feature(TEXT_DOCUMENT_DID_CLOSE)
    @error_logger
    def did_close(ls: LanguageServer, params: DidCloseTextDocumentParams):
        path = unquote(params.text_document.uri)
        ls.show_message_log(f"Did Close: {path}")
        hover_cache.pop(params.text_document.uri, {})
        dependency_cache.pop(params.text_document.uri, {})
        for cache in dependency_cache.values():
            if path in cache:
                cache.remove(path)

    @server.feature(TEXT_DOCUMENT_DID_OPEN)
    @error_logger
    def did_open(ls, params: DidOpenTextDocumentParams):
        ls.show_message_log(f"Did Open: {unquote(params.text_document.uri)}")
        validate(ls, params.text_document.uri)

    @server.feature(TEXT_DOCUMENT_HOVER)
    @error_logger
    def hover(ls, params: HoverParams):
        row = params.position.line + 1
        col = params.position.character
        uri = params.text_document.uri
        ls.show_message_log(f"Hover request in {unquote(uri)}: {row}, {col}")

        cache_entry: TypeReference | None = hover_cache[uri].get(row, {}).get(col, None)
        if cache_entry and cache_entry.type_def and cache_entry.type_def.comment:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=cache_entry.type_def.comment
                ),
                range=Range(
                    start=Position(cache_entry.position.start.line - 1, cache_entry.position.start.col),
                    end=Position(cache_entry.position.end.line - 1, cache_entry.position.end.col)
                )
            )

    @server.feature(TEXT_DOCUMENT_DEFINITION)
    @error_logger
    def definition(ls, params: DefinitionParams):
        row = params.position.line + 1
        col = params.position.character
        ls.show_message_log(f"Go To Definition request: {row}, {col}")
        cache_entry: TypeReference | None = hover_cache[params.text_document.uri].get(row, {}).get(col, None)
        if cache_entry and cache_entry.type_def and isinstance(cache_entry.type_def,
                                                               BaseType) and cache_entry.type_def.position.file:
            return Location(
                uri=cache_entry.type_def.position.file.as_uri(),
                range=Range(
                    start=Position(cache_entry.type_def.position.start.line - 1,
                                   cache_entry.type_def.position.start.col),
                    end=Position(cache_entry.type_def.position.end.line - 1, cache_entry.type_def.position.end.col)
                )
            )

    @server.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES)
    @error_logger
    def did_change_watched_files(ls, params: DidChangeWatchedFilesParams):
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
