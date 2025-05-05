# Copyright 2024 - 2025 jothepro
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

import re
from typing import cast
import uuid
from importlib.metadata import version
from urllib.parse import unquote
from pygls.workspace.text_document import TextDocument
from lsprotocol.types import *
from pydjinni.parser.base_models import TypeReference, FileReference
from .tolerant_converter import tolerant_converter
from pydjinni_language_server.api import Configuration, LanguageServerAPI
from pydjinni_language_server.language_server import PyDjinniLanguageServer
from .comment_renderer import HoverTooltipCommentRenderer
from .util import (
    identifier_range,
    map_completion_item_description,
    map_completion_item_kind,
    to_diagnostics,
    to_document_symbol,
    to_range,
    type_range,
    map_kind,
)


api: LanguageServerAPI = LanguageServerAPI()


server = PyDjinniLanguageServer(
    name="pydjinni-language-server", version=version("pydjinni"), converter_factory=tolerant_converter
)


async def configure(ls: PyDjinniLanguageServer, configurations: list[Configuration]):
    for workspace, configuration in zip(api.workspaces, configurations):
        workspace.configure(configuration)
        await ls.update_workspace_capabilities(workspace)


@server.feature(INITIALIZE)
def initialize(ls: PyDjinniLanguageServer, params: InitializeParams):
    ls.show_message_log(f"[{INITIALIZE}] Initializing PyDjinni language server {version('pydjinni')}")
    if ls.client_capabilities.workspace and ls.client_capabilities.workspace.workspace_folders:
        ls.show_message_log(f"[{INITIALIZE}] Multiroot support detected")
        for folder in ls.workspace.folders:
            ls.show_message_log(f"[{INITIALIZE}] Adding workspace folder: {folder}")
            api.add_workspace(folder)
    elif ls.workspace.root_uri:
        ls.show_message_log(f"[{INITIALIZE}] Configuring project root: {ls.workspace.root_uri}")
        api.add_workspace(ls.workspace.root_uri)


@server.feature(INITIALIZED)
async def initialized(ls: PyDjinniLanguageServer, params: InitializedParams):
    ls.show_message_log(f"[{INITIALIZED}] Registering Capabilities")

    await ls.register_capability_async(
        RegistrationParams(
            registrations=[
                Registration(
                    id=str(uuid.uuid4()),
                    method=WORKSPACE_DID_CHANGE_CONFIGURATION,
                    register_options=DidChangeConfigurationRegistrationOptions(section="pydjinni"),
                )
            ]
        )
    )

    for workspace in api.workspaces:
        await ls.register_workspace_capabilites(workspace)

    if ls.client_capabilities.workspace and ls.client_capabilities.workspace.configuration:
        configurations = Configuration.from_response(
            await ls.get_configuration_async(
                WorkspaceConfigurationParams(
                    [
                        ConfigurationItem(section="pydjinni", scope_uri=workspace.root_uri)
                        for workspace in api.workspaces
                    ]
                )
            )
        )
        await configure(ls, configurations)


@server.feature(WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS)
async def did_change_workspace_folders(ls: PyDjinniLanguageServer, params: DidChangeWorkspaceFoldersParams):
    for added in params.event.added:
        workspace = api.add_workspace(added.uri)
        await ls.register_workspace_capabilites(workspace)
        ls.show_message_log(f"[{WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS}] Added workspace folder: {added.uri}")
    for removed in params.event.removed:
        workspace = api.remove_workspace(removed.uri)
        if workspace:
            await ls.unregister_workspace_capabilities(workspace)
        ls.show_message_log(f"[{WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS}] Removed workspace folder: {removed.uri}")


@server.feature(WORKSPACE_DID_CHANGE_CONFIGURATION)
async def did_change_configuration(ls: PyDjinniLanguageServer, params: DidChangeConfigurationParams):
    ls.show_message_log(f"[{WORKSPACE_DID_CHANGE_CONFIGURATION}] configuration changed")
    if ls.client_capabilities.workspace and ls.client_capabilities.workspace.configuration:
        configurations = Configuration.from_response(
            await ls.get_configuration_async(
                WorkspaceConfigurationParams(
                    [
                        ConfigurationItem(section="pydjinni", scope_uri=workspace.root_uri)
                        for workspace in api.workspaces
                    ]
                )
            )
        )
        await configure(ls, configurations)
    else:
        configurations = Configuration.from_response([cast(dict, params.settings)["pydjinni"]])
        await configure(ls, configurations)
    for uri in ls.workspace.documents.keys():
        diagnostics = await api.get_workspace(uri).validate(ls.get_text_document_path(uri))
        ls.publish_diagnostics(uri=uri, diagnostics=to_diagnostics(diagnostics))

    ls.request_code_lens_refresh()


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: PyDjinniLanguageServer, params: DidChangeTextDocumentParams):
    ls.show_message_log(f"[{TEXT_DOCUMENT_DID_CHANGE}] {params.text_document.uri}")
    diagnostics = await api.get_workspace(params.text_document.uri).validate(
        ls.get_text_document_path(params.text_document.uri)
    )
    ls.publish_diagnostics(
        uri=params.text_document.uri,
        diagnostics=to_diagnostics(diagnostics),
        version=params.text_document.version,
    )


@server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: PyDjinniLanguageServer, params: DidCloseTextDocumentParams):
    ls.show_message_log(f"[{TEXT_DOCUMENT_DID_CLOSE}] {params.text_document.uri}")
    api.get_workspace(params.text_document.uri).reset_cache(params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: PyDjinniLanguageServer, params: DidOpenTextDocumentParams):
    ls.show_message_log(f"[{TEXT_DOCUMENT_DID_OPEN}] {params.text_document.uri}")
    diagnostics = await api.get_workspace(params.text_document.uri).validate(
        ls.get_text_document_path(params.text_document.uri)
    )
    ls.publish_diagnostics(
        uri=params.text_document.uri,
        diagnostics=to_diagnostics(diagnostics),
        version=params.text_document.version,
    )


@server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: PyDjinniLanguageServer, params: DidSaveTextDocumentParams):
    ls.show_message_log(f"[{TEXT_DOCUMENT_DID_SAVE}] {params.text_document.uri}")
    await api.get_workspace(params.text_document.uri).generate_on_save(
        ls.get_text_document_path(params.text_document.uri)
    )
    ls.request_code_lens_refresh()


@server.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES)
async def did_change_watched_files(ls: PyDjinniLanguageServer, params: DidChangeWatchedFilesParams):
    for change in params.changes:
        ls.show_message_log(f"[{WORKSPACE_DID_CHANGE_WATCHED_FILES}] {change.uri}")
        workspace = api.get_workspace(change.uri)
        if change.type == FileChangeType.Deleted:
            workspace.reset_cache(change.uri)

        change_uri = unquote(change.uri)
        if change_uri == (workspace.root_path / workspace.configuration.config).absolute().as_uri():
            workspace.configure()
            ls.request_code_lens_refresh()
        for uri, dependencies in workspace.dependency_cache.items():
            if change_uri in dependencies:
                diagnostics = await workspace.validate(ls.get_text_document_path(uri))
                ls.publish_diagnostics(uri=uri, diagnostics=to_diagnostics(diagnostics))


@server.feature(TEXT_DOCUMENT_HOVER)
async def hover(ls: PyDjinniLanguageServer, params: HoverParams):
    ls.show_message_log(
        f"[{TEXT_DOCUMENT_HOVER}] {params.text_document.uri}: {params.position.character}, {params.position.line}"
    )
    cache_entry = await api.get_workspace(params.text_document.uri).get_hover(
        row=params.position.line, col=params.position.character, uri=params.text_document.uri
    )
    if cache_entry:
        comment: str | None = None
        if isinstance(cache_entry, FileReference):
            comment = f"```txt\n{cache_entry.path}\n```"
        elif isinstance(cache_entry, TypeReference) and cache_entry.type_def and cache_entry.type_def._parsed_comment:
            comment = HoverTooltipCommentRenderer().render_tokens(*cache_entry.type_def._parsed_comment)
        elif not isinstance(cache_entry, TypeReference) and cache_entry._parsed_comment:
            comment = HoverTooltipCommentRenderer().render_tokens(*cache_entry._parsed_comment)
        if comment:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=comment,
                ),
                range=identifier_range(cache_entry),
            )


@server.feature(TEXT_DOCUMENT_DEFINITION)
async def definition(ls: PyDjinniLanguageServer, params: DefinitionParams) -> list[LocationLink | Location]:
    ls.show_message_log(
        f"[{TEXT_DOCUMENT_DEFINITION}] {params.text_document.uri}: {params.position.character}, {params.position.line}"
    )
    link_support = (
        ls.client_capabilities.text_document
        and ls.client_capabilities.text_document.type_definition
        and ls.client_capabilities.text_document.type_definition.link_support
    )

    definitions = api.get_workspace(params.text_document.uri).get_definitions(
        row=params.position.line, col=params.position.character, uri=params.text_document.uri
    )

    result: list[LocationLink | Location] = []
    async for definition in definitions:
        target_uri = definition.target_position.file.as_uri()
        target_range = to_range(definition.target_position)
        ls.show_message_log(
            f"[{TEXT_DOCUMENT_DEFINITION}] link: {target_uri}: {target_range.start.line}, {target_range.end.line}"
        )
        if link_support:
            result.append(
                LocationLink(
                    target_uri=target_uri,
                    target_range=target_range,
                    target_selection_range=to_range(definition.target_selection),
                    origin_selection_range=to_range(definition.origin_position),
                )
            )

        else:
            result.append(Location(uri=target_uri, range=target_range))
    return result


@server.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
async def document_symbol(
    ls: PyDjinniLanguageServer, params: DocumentSymbolParams
) -> list[SymbolInformation | DocumentSymbol]:
    ls.show_message_log(f"[{TEXT_DOCUMENT_DOCUMENT_SYMBOL}] {params.text_document.uri}")
    workspace = api.get_workspace(params.text_document.uri)
    if (
        ls.client_capabilities.text_document
        and ls.client_capabilities.text_document.document_symbol
        and ls.client_capabilities.text_document.document_symbol.hierarchical_document_symbol_support
    ):
        return [
            to_document_symbol(type_def)
            for type_def in await workspace.get_all_document_symbols(params.text_document.uri)
        ]
    else:
        return [
            SymbolInformation(
                name=type_def.name,
                location=Location(uri=params.text_document.uri, range=type_range(type_def)),
                kind=map_kind(type_def),
                deprecated=type_def.deprecated != False,
                container_name=".".join(type_def.namespace),
            )
            async for type_def in workspace.get_type_document_symbols(params.text_document.uri)
        ]


@server.feature(TEXT_DOCUMENT_CODE_LENS)
async def code_lense(ls: PyDjinniLanguageServer, params: CodeLensParams) -> list[CodeLens]:
    ls.show_message_log(f"[{TEXT_DOCUMENT_CODE_LENS}] {params.text_document.uri}")
    sources = api.get_workspace(params.text_document.uri).get_generated_sources(params.text_document.uri)
    return [
        CodeLens(
            range=identifier_range(source.type_def),
            command=Command(
                title=source.language,
                command="open_generated_interface",
                arguments=[source.uri],
            ),
        )
        async for source in sources
    ]


@server.command("open_generated_interface")
async def execute_command(ls: PyDjinniLanguageServer, arguments: list[str]):
    uri = unquote(arguments[0])
    await ls.show_document_async(ShowDocumentParams(uri=uri))


@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["+", "-"]))
async def completion(ls: PyDjinniLanguageServer, params: CompletionParams) -> list[CompletionItem] | None:
    text_document: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    line = text_document.lines[params.position.line][: params.position.character]
    ls.show_message_log(f"[{TEXT_DOCUMENT_COMPLETION}] {params.text_document.uri} {line}")
    error_pattern = re.compile(r"(throws *[\w.]*, *[\w.]*$)|(throws *[\w.]*$)")
    type_pattern = re.compile(r"(: *[\w.]*$)|(-> *[\w.]*$)|([\w.] *< *[\w.]*$)|([\w.] *< *[\w.]* *, *[\w.]*$)")
    target_pattern = re.compile(r" +[-\+]\w*$")
    error_completion = re.findall(error_pattern, line)
    type_completion = re.findall(type_pattern, line)
    target_completion = re.findall(target_pattern, line)
    if error_completion or type_completion or target_completion:
        workspace = api.get_workspace(params.text_document.uri)
        if error_completion or type_completion:
            type_defs = (
                workspace.get_all_completion_type_defs(params.text_document.uri)
                if type_completion
                else workspace.get_all_error_domains(params.text_document.uri)
            )
            return [
                CompletionItem(
                    label=".".join(type_def.namespace + [type_def.name]),
                    label_details=CompletionItemLabelDetails(description=map_completion_item_description(type_def)),
                    kind=map_completion_item_kind(type_def),
                    tags=[CompletionItemTag.Deprecated] if type_def.deprecated else None,
                    detail=map_completion_item_description(type_def),
                    documentation=(
                        MarkupContent(
                            kind=MarkupKind.Markdown,
                            value=HoverTooltipCommentRenderer().render_tokens(*type_def._parsed_comment),
                        )
                        if type_def._parsed_comment
                        else None
                    ),
                    deprecated=type_def.deprecated != False,
                )
                for type_def in await type_defs
            ]
        elif target_completion:
            return [
                CompletionItem(
                    label=target.key,
                    label_details=CompletionItemLabelDetails(description=target.display_key),
                    detail=target.display_key,
                )
                for target in workspace.get_all_target_languages()
            ]
