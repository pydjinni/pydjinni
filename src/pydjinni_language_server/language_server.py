# Copyright 2024 jothepro
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

import json
import logging
import os
import uuid
from importlib.metadata import version
from pathlib import Path
from urllib.parse import unquote, urlparse

import click
from lsprotocol.types import *
from pydjinni import API
from pydjinni.defs import DEFAULT_CONFIG_PATH
from pydjinni.exceptions import ApplicationException, ConfigurationException
from pydjinni.generator.target import Target
from pydjinni.parser.ast import (
    Interface,
    Record,
    Function,
    Enum,
    ErrorDomain,
    Flags,
    Namespace
)
from pydjinni.parser.base_models import TypeReference, BaseType, SymbolicConstantType, BaseField
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
@click.option('--generate-on-save', '-g', is_flag=True, help="If enabled, the generator will run on file save.")
@click.option('--log', '-l', default=None, type=Path, help="Log file for the Language Server.")
def start(connection, host: str, port: int, config: Path, generate_on_save: bool, log: Path):
    """
    Start a Language Server
    """
    server = LanguageServer("pydjinni-language-server", version('pydjinni'), converter_factory=tolerant_converter)
    if log:
        logging.basicConfig(filename=log, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

    ast_cache: dict[str, list[BaseType | Namespace]] = {}
    type_def_cache: dict[str, list[BaseType]] = {}
    hover_cache: dict[str, dict[int, dict[int, TypeReference]]] = {}
    dependency_cache: dict[str, set[str]] = {}
    configured_targets_cache: list[Target] = []
    if config.exists():
        api = API().configure(path=config)
        configured_targets_cache = api.configured_targets
    else:
        api = API().configure(options={
            "generate": {}
        })


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

    def type_range(definition: BaseField | BaseType) -> Range:
        return Range(
            start=Position(definition.position.start.line - 1, definition.position.start.col),
            end=Position(definition.position.end.line - 1, definition.position.end.col)
        )


    def validate(ls, uri):
        ls.show_message_log(f"Validating {unquote(uri)}")
        document: TextDocument = ls.workspace.get_text_document(uri)
        error_items = []
        refs = []
        path = TextDocumentPath(document)
        nonlocal configured_targets_cache
        try:
            generate_context = api.parse(path)
            refs = generate_context.refs

            ast_cache[uri] = [type_def for type_def in generate_context.ast if
                              type_def.position.file.as_uri() == uri]
            type_def_cache[uri] = [type_def for type_def in generate_context.defs if
                              type_def.position.file.as_uri() == uri]
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
    def init(ls, _: InitializedParams):
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
                            ),
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
        ast_cache.pop(params.text_document.uri, {})
        type_def_cache.pop(params.text_document.uri, {})
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
                range=type_range(cache_entry)
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
                range=type_range(cache_entry.type_def)
            )

    @server.feature(TEXT_DOCUMENT_CODE_ACTION)
    @error_logger
    def code_action(ls, params: CodeActionParams):
        pass

    @server.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
    @error_logger
    def document_symbol(ls: LanguageServer, params: DocumentSymbolParams):
        ls.show_message_log(f"Document symbol request: {unquote(params.text_document.uri)}")
        def map_kind(type_def):
            if isinstance(type_def, Interface):
                return SymbolKind.Interface
            elif isinstance(type_def, Record) or isinstance(type_def, ErrorDomain):
                return SymbolKind.Struct
            elif isinstance(type_def, Function):
                return SymbolKind.Function
            elif isinstance(type_def, SymbolicConstantType):
                return SymbolKind.Enum
            else:
                return SymbolKind.Null

        def to_document_symbol(type_def):
            if isinstance(type_def, Namespace):
                return DocumentSymbol(
                    name=type_def.name,
                    kind=SymbolKind.Namespace,
                    range=type_range(type_def),
                    selection_range=type_range(type_def),
                    children=[to_document_symbol(child) for child in type_def.children]
                )
            elif isinstance(type_def, Interface):
                return DocumentSymbol(
                    name=type_def.name,
                    kind=SymbolKind.Interface,
                    range=type_range(type_def),
                    selection_range=type_range(type_def),
                    deprecated=type_def.deprecated != False,
                    detail="interface",
                    children=[
                        DocumentSymbol(
                            name=method.name,
                            kind=SymbolKind.Method,
                            range=type_range(method),
                            selection_range=type_range(method),
                            deprecated=method.deprecated != False,
                            detail=method.return_type_ref.name if method.return_type_ref else None,
                            children=[
                                DocumentSymbol(
                                    name=parameter.name,
                                    kind=SymbolKind.Variable,
                                    range=type_range(parameter),
                                    selection_range=type_range(parameter),
                                    detail=parameter.type_ref.name
                                )
                                for parameter in method.parameters
                            ]
                        ) for method in type_def.methods
                    ]
                )
            elif isinstance(type_def, Record):
                return DocumentSymbol(
                    name=type_def.name,
                    kind=SymbolKind.Class,
                    range=type_range(type_def),
                    selection_range=type_range(type_def),
                    deprecated=type_def.deprecated != False,
                    detail="record",
                    children=[
                        DocumentSymbol(
                            name=field.name,
                            kind=SymbolKind.Field,
                            range=type_range(field),
                            selection_range=type_range(field),
                            detail=field.type_ref.name
                        ) for field in type_def.fields
                    ]
                )
            elif isinstance(type_def, Enum):
                return DocumentSymbol(
                    name=type_def.name,
                    kind=SymbolKind.Enum,
                    range=type_range(type_def),
                    selection_range=type_range(type_def),
                    deprecated=type_def.deprecated != False,
                    detail="enum",
                    children=[
                        DocumentSymbol(
                            name=item.name,
                            kind=SymbolKind.EnumMember,
                            range=type_range(item),
                            selection_range=type_range(item)
                        ) for item in type_def.items
                    ]
                )
            elif isinstance(type_def, Flags):
                return DocumentSymbol(
                    name=type_def.name,
                    kind=SymbolKind.Enum,
                    range=type_range(type_def),
                    selection_range=type_range(type_def),
                    deprecated=type_def.deprecated != False,
                    detail="flags",
                    children=[
                        DocumentSymbol(
                            name=flag.name,
                            kind=SymbolKind.EnumMember,
                            range=type_range(flag),
                            selection_range=type_range(flag),
                            detail="all" if flag.all else "none" if flag.none else None
                        ) for flag in type_def.flags
                    ]
                )
            elif isinstance(type_def, ErrorDomain):
                return DocumentSymbol(
                    name=type_def.name,
                    kind=SymbolKind.Class,
                    range=type_range(type_def),
                    selection_range=type_range(type_def),
                    deprecated=type_def.deprecated != False,
                    detail="error",
                    children=[
                        DocumentSymbol(
                            name=error_code.name,
                            kind=SymbolKind.Field,
                            range=type_range(error_code),
                            selection_range=type_range(error_code),
                            children=[
                                DocumentSymbol(
                                    name=parameter.name,
                                    kind=SymbolKind.Variable,
                                    range=type_range(parameter),
                                    selection_range=type_range(parameter),
                                    detail=parameter.type_ref.name
                                ) for parameter in error_code.parameters
                            ]
                        ) for error_code in type_def.error_codes
                    ]
                )
            elif isinstance(type_def, Function):
                return DocumentSymbol(
                    name="<anonymous>" if type_def.anonymous else type_def.name,
                    kind=SymbolKind.Function,
                    range=type_range(type_def),
                    selection_range=type_range(type_def),
                    deprecated=type_def.deprecated != False,
                    detail="function",
                    children=[
                        DocumentSymbol(
                            name=parameter.name,
                            kind=SymbolKind.Variable,
                            range=type_range(parameter),
                            selection_range=type_range(parameter),
                            detail=parameter.type_ref.name
                        )
                        for parameter in type_def.parameters
                    ]
                )
            else:
                return DocumentSymbol(
                    name=type_def.name,
                    kind=map_kind(type_def),
                    range=type_range(type_def),
                    selection_range=type_range(type_def)
                )
        if params.text_document.uri in ast_cache:
            if ls.client_capabilities.text_document.document_symbol.hierarchical_document_symbol_support:
                return [to_document_symbol(type_def) for type_def in ast_cache[params.text_document.uri]]
            else:
                return [SymbolInformation(
                    name=type_def.name,
                    location=Location(
                        uri=params.text_document.uri,
                        range=type_range(type_def)
                    ),
                    kind=map_kind(type_def),
                    deprecated=type_def.deprecated != False,
                    container_name=".".join(type_def.namespace)
                ) for type_def in type_def_cache[params.text_document.uri] if not isinstance(type_def, Function) or not type_def.anonymous]

    @server.feature(TEXT_DOCUMENT_CODE_LENS)
    @error_logger
    def code_lense(ls, params: CodeLensParams):
        ls.show_message_log(f"code lense request: {params.text_document.uri}")
        lenses: list[CodeLens] = []
        for target in configured_targets_cache:
            main_generator = [generator for generator in target.generator_instances if generator.key == target.key][0]
            for type_def in type_def_cache[params.text_document.uri]:
                if not isinstance(type_def, Function) or not type_def.anonymous:
                    if hasattr(type_def, target.key):
                        target_type = getattr(type_def, target.key)
                        if hasattr(target_type, "header"):
                            file_output_path: Path = main_generator.header_path / target_type.header
                        else:
                            file_output_path: Path = main_generator.source_path / target_type.source
                        line = (type_def.position.start.line + (len(type_def.comment.split("\n")) if type_def.comment else 0)) - 1
                        lenses.append(CodeLens(
                            range=Range(
                                start=Position(line, 0),
                                end=Position(line, 5)
                            ),
                            command=Command(
                                title=target.display_key,
                                command="open_generated_interface",
                                arguments=[file_output_path.absolute().as_uri(), target.display_key, type_def.name]
                            )
                        ))
        return lenses

    @server.command("open_generated_interface")
    @error_logger
    def execute_command(ls: LanguageServer, arguments):
        file_path = arguments[0]
        target_language = arguments[1]
        type_def_name = arguments[2]
        if Path(unquote(urlparse(file_path).path)).exists():
            ls.show_message_log(f"Command: Open generated interface {file_path}")
            ls.show_document_async(ShowDocumentParams(
                uri=file_path
            ))
        else:
            ls.show_message_log(f"Command: Open generated interface failed. Cannot find {file_path}")
            ls.show_message(f"Cannot find generated {target_language} interface for {type_def_name}.", msg_type=MessageType.Error)


    @server.feature(TEXT_DOCUMENT_DID_SAVE)
    @error_logger
    def did_save(ls, params: DidSaveTextDocumentParams):
        ls.show_message_log(f"File saved: {params.text_document.uri}")
        if generate_on_save:
            ls.show_message_log(f"Generating interfaces for {params.text_document.uri}")
            context = api.parse(TextDocumentPath(ls.workspace.get_text_document(params.text_document.uri)))
            for target in configured_targets_cache:
                context.generate(target.key)


    @server.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES)
    @error_logger
    def did_change_watched_files(ls: LanguageServer, params: DidChangeWatchedFilesParams):
        for change in params.changes:
            path = unquote(change.uri)
            if change.uri == config.absolute().as_uri():
                nonlocal api
                nonlocal configured_targets_cache
                api = API().configure(path=config)
                configured_targets_cache = api.configured_targets
                ls.lsp.send_request(WORKSPACE_CODE_LENS_REFRESH)
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
