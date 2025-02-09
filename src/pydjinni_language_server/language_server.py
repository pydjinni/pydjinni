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

import logging
import os
import uuid
from importlib.metadata import version
from pathlib import Path
from urllib.parse import unquote

from lsprotocol.types import *
from pygls.server import LanguageServer
from pygls.workspace import TextDocument

from pydjinni.exceptions import ConfigurationException
from pydjinni.parser.ast import Function, Namespace
from pydjinni.parser.base_models import TypeReference, BaseType
from pydjinni.parser.parser import Parser
from pydjinni_language_server.text_document_path import TextDocumentPath
from .error_logger import error_logger
from .tolerant_converter import tolerant_converter
from .util import to_document_symbol, type_range, map_kind, configure_api, to_hover_cache, to_diagnostic

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11

logger = logging.getLogger(__name__)


def init_language_server(config: Path, generate_on_save: bool, generate_base_path: Path, log: Path):
    server = LanguageServer("pydjinni-language-server", version('pydjinni'), converter_factory=tolerant_converter)
    if log:
        logging.basicConfig(filename=log, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

    ast_cache: dict[str, list[BaseType | Namespace]] = {}
    type_def_cache: dict[str, list[BaseType]] = {}
    hover_cache: dict[str, dict[int, dict[int, TypeReference]]] = {}
    dependency_cache: dict[str, set[str]] = {}
    api = configure_api(config)

    def validate(ls, uri):
        ls.show_message_log(f"Validating {unquote(uri)}")
        document: TextDocument = ls.workspace.get_text_document(uri)
        error_items = []
        refs = []
        path = TextDocumentPath(document)
        try:
            generate_context = api.parse(path)
            refs = generate_context.refs

            ast_cache[uri] = [type_def for type_def in generate_context.ast if
                              type_def.position.file.as_uri() == uri]
            type_def_cache[uri] = [type_def for type_def in generate_context.defs if
                                   type_def.position.file.as_uri() == uri]
        except Parser.ParsingExceptionList as e:
            error_items = [to_diagnostic(error, DiagnosticSeverity.Error, f"{error.__doc__}: {error.description}") for
                           error in e.items
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
                if isinstance(ref.type_def.deprecated, str):
                    message = f"deprecated: {ref.type_def.deprecated}"
                else:
                    message = "deprecated"
                error_items.append(to_diagnostic(ref, DiagnosticSeverity.Warning, message))

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
    def init(ls: LanguageServer, _: InitializedParams):
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
    def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
        ls.show_message_log(f"[{TEXT_DOCUMENT_DID_CHANGE}] {unquote(params.text_document.uri)}")
        validate(ls, params.text_document.uri)

    @server.feature(TEXT_DOCUMENT_DID_CLOSE)
    @error_logger
    def did_close(ls: LanguageServer, params: DidCloseTextDocumentParams):
        path = unquote(params.text_document.uri)
        ls.show_message_log(f"[{TEXT_DOCUMENT_DID_CLOSE}] {path}")
        hover_cache.pop(params.text_document.uri, {})
        dependency_cache.pop(params.text_document.uri, {})
        ast_cache.pop(params.text_document.uri, {})
        type_def_cache.pop(params.text_document.uri, {})
        for cache in dependency_cache.values():
            if path in cache:
                cache.remove(path)

    @server.feature(TEXT_DOCUMENT_DID_OPEN)
    @error_logger
    def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
        ls.show_message_log(f"[{TEXT_DOCUMENT_DID_OPEN}] {unquote(params.text_document.uri)}")
        validate(ls, params.text_document.uri)

    @server.feature(TEXT_DOCUMENT_HOVER)
    @error_logger
    def hover(ls: LanguageServer, params: HoverParams):
        row = params.position.line + 1
        col = params.position.character
        uri = params.text_document.uri
        ls.show_message_log(f"[{TEXT_DOCUMENT_HOVER}] {unquote(uri)}: {row}, {col}")

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
    def definition(ls: LanguageServer, params: DefinitionParams):
        row = params.position.line + 1
        col = params.position.character
        ls.show_message_log(f"[{TEXT_DOCUMENT_DEFINITION}] {row}, {col}")
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
        ls.show_message_log(f"[{TEXT_DOCUMENT_DOCUMENT_SYMBOL}] {unquote(params.text_document.uri)}")

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
                ) for type_def in type_def_cache[params.text_document.uri] if
                    not isinstance(type_def, Function) or not type_def.anonymous]

    @server.feature(TEXT_DOCUMENT_CODE_LENS)
    @error_logger
    def code_lense(ls: LanguageServer, params: CodeLensParams):
        ls.show_message_log(f"[{TEXT_DOCUMENT_CODE_LENS}] {params.text_document.uri}")
        lenses: list[CodeLens] = []
        for target in api.configured_targets:
            main_generator = [generator for generator in target.generator_instances if generator.key == target.key][0]
            for type_def in type_def_cache[params.text_document.uri]:
                if not isinstance(type_def, Function) or not type_def.anonymous:
                    if hasattr(type_def, target.key):
                        target_type = getattr(type_def, target.key)
                        if hasattr(target_type, "header"):
                            file_output_path: Path = generate_base_path / main_generator.header_path / target_type.header
                        else:
                            file_output_path: Path = generate_base_path / main_generator.source_path / target_type.source
                        line = (type_def.position.start.line + (
                            len(type_def.comment.split("\n")) if type_def.comment else 0)) - 1
                        generated_file_path = file_output_path.absolute()
                        if generated_file_path.exists():
                            lenses.append(CodeLens(
                                range=Range(
                                    start=Position(line, type_def.position.start.col),
                                    end=Position(line, type_def.position.start.col + 5)
                                ),
                                command=Command(
                                    title=target.display_key,
                                    command="open_generated_interface",
                                    arguments=[generated_file_path.as_uri()]
                                )
                            ))
        return lenses

    @server.command("open_generated_interface")
    @error_logger
    def execute_command(ls: LanguageServer, arguments):
        file_path = arguments[0]
        ls.show_message_log(f"[command/open_generated_interface] {file_path}")
        ls.show_document_async(ShowDocumentParams(
            uri=file_path
        ))

    @server.feature(TEXT_DOCUMENT_DID_SAVE)
    @error_logger
    def did_save(ls, params: DidSaveTextDocumentParams):
        ls.show_message_log(f"[{TEXT_DOCUMENT_DID_SAVE}] {params.text_document.uri}")
        if generate_on_save:
            ls.show_message_log(f"[{TEXT_DOCUMENT_DID_SAVE}] Generating interfaces for {params.text_document.uri}")
            generate_base_path.mkdir(parents=True, exist_ok=True)
            prev_cwd = Path.cwd()
            if generate_base_path.absolute().is_relative_to(prev_cwd.absolute()):
                os.chdir(generate_base_path)
                try:
                    context = api.parse(TextDocumentPath(ls.workspace.get_text_document(params.text_document.uri)))
                    for target in api.configured_targets:
                        context.generate(target.key, clean=True)
                finally:
                    os.chdir(prev_cwd)

    @server.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES)
    @error_logger
    def did_change_watched_files(ls: LanguageServer, params: DidChangeWatchedFilesParams):
        for change in params.changes:
            path = unquote(change.uri)
            if change.uri == config.absolute().as_uri():
                nonlocal api
                api = configure_api(config)
                ls.lsp.send_request(WORKSPACE_CODE_LENS_REFRESH)
            ls.show_message_log(f"[{WORKSPACE_DID_CHANGE_WATCHED_FILES}] {path}")
            ls.show_message_log(
                f"[{WORKSPACE_DID_CHANGE_WATCHED_FILES}] Searching for dependents that need updating...")
            for uri, dependencies in dependency_cache.items():
                if path in dependencies:
                    validate(ls, uri)

    return server
