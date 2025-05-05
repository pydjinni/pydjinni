import asyncio
import logging
from pathlib import Path
from typing import Any, AsyncGenerator, Generator
from urllib.parse import unquote
import uuid

from pydjinni.api import API
from pydjinni.builder.target import BuildTarget
from pydjinni.generator.target import Target
from pydjinni.parser.ast import ErrorDomain, Function, Namespace
from pydjinni.parser.base_models import BaseExternalType, BaseField, BaseType, FileReference, TypeReference
from pydjinni.parser.parser import Parser
from pydjinni.position import Cursor, Position
from pydjinni_language_server.models import Configuration, Diagnostics, GeneratedSource, ReferenceLocationLink
from pydjinni_language_server.text_document_path import TextDocumentPath
from pydjinni_language_server.util import to_hover_cache


class Workspace:
    def __init__(self, root_uri: str):
        self.uuid = uuid.uuid4()
        self.root_uri = unquote(root_uri)
        self.root_path = Path.from_uri(root_uri)
        self.api = API(root_path=self.root_path)
        self.ast_cache: dict[str, list[BaseType | Namespace]] = {}
        self.type_def_cache: dict[str, list[BaseType]] = {}
        self.hover_cache: dict[
            str, dict[int, dict[int, TypeReference | FileReference | BaseField | Namespace | BaseType]]
        ] = {}
        self.dependency_cache: dict[str, set[str]] = {}
        self.configuration = Configuration()
        self.configured_event = asyncio.Event()
        self.generate_context: dict[str, API.ConfiguredContext.GenerateContext] = {}
        self.validated_event = asyncio.Event()

    def configure(self, configuration: Configuration | None = None):
        if configuration:
            self.configuration = configuration
        absolute_config = self.configuration.config if self.configuration.config.is_absolute() else self.root_path / self.configuration.config
        if absolute_config.exists():
            self.configured_context = self.api.configure(path=absolute_config)
        else:
            self.configured_context = self.api.configure(options={"generate": {}})
        self.configured_event.set()

    def reset_cache(self, uri: str):
        uri = unquote(uri)
        self.hover_cache.pop(uri)
        self.dependency_cache.pop(uri)
        self.ast_cache.pop(uri)
        self.type_def_cache.pop(uri)
        self.generate_context.pop(uri)
        for cache in self.dependency_cache.values():
            if uri in cache:
                cache.remove(uri)

    async def validate(self, document: TextDocumentPath) -> Diagnostics:
        await self.configured_event.wait()
        errors: list[Diagnostics.DiagnosticItem] = []
        warnings: list[Diagnostics.DiagnosticItem] = []
        results: API.ConfiguredContext.GenerateContext | Parser.ParsingExceptionList
        uri = document.as_uri()
        try:
            results = self.configured_context.parse(document)
            self.generate_context[uri] = results
        except Parser.ParsingExceptionList as e:
            results = e
            for error in e.items:
                if error.position.file.as_uri() == uri:
                    errors.append(
                        Diagnostics.DiagnosticItem(definition=error, message=f"{error.__doc__}: {error.description}")
                    )
        self.ast_cache[uri] = [
            type_def for type_def in results.ast if type_def.position and type_def.position.file.as_uri() == uri
        ]
        self.type_def_cache[uri] = [
            type_def for type_def in results.type_defs if type_def.position and type_def.position.file.as_uri() == uri
        ]
        for type_ref in results.type_refs:
            if type_ref.position.file.as_uri() == uri and type_ref.type_def and type_ref.type_def.deprecated:
                message = "deprecated"
                if isinstance(type_ref.type_def.deprecated, str):
                    message += f": {type_ref.type_def.deprecated}"
                warnings.append(Diagnostics.DiagnosticItem(type_ref, message))

        self.hover_cache[uri] = to_hover_cache(
            [
                ref
                for ref in results.type_refs + results.file_imports + results.fields + results.ast
                if ref.position and ref.position.file.as_uri() == uri
            ],
        )

        self.dependency_cache[uri] = set(
            [
                ref.type_def.position.file.as_uri()
                for ref in results.type_refs
                if ref.type_def and ref.type_def.position and ref.type_def.position.file.as_uri() != uri
            ]
            + [(self.root_path / self.configuration.config).absolute().as_uri()]
        )

        self.validated_event.set()

        return Diagnostics(errors, warnings)

    async def get_hover(
        self, row: int, col: int, uri: str
    ) -> TypeReference | FileReference | BaseField | Namespace | BaseType | None:
        await self.validated_event.wait()
        return self.hover_cache[unquote(uri)].get(row, {}).get(col)

    async def get_definitions(self, row: int, col: int, uri: str) -> AsyncGenerator[ReferenceLocationLink]:
        await self.validated_event.wait()
        cache_entry = self.hover_cache[unquote(uri)].get(row, {}).get(col)
        if cache_entry:
            if isinstance(cache_entry, FileReference):
                yield ReferenceLocationLink(
                    target_position=Position(start=Cursor(), end=Cursor(), file=cache_entry.path),
                    target_selection=Position(start=Cursor(), end=Cursor(), file=cache_entry.path),
                    origin_position=cache_entry.identifier_position,
                )
            elif (
                isinstance(cache_entry, TypeReference)
                and cache_entry.type_def
                and cache_entry.type_def.position
                and cache_entry.type_def.identifier_position
            ):
                yield ReferenceLocationLink(
                    target_position=cache_entry.type_def.position,
                    target_selection=cache_entry.type_def.identifier_position,
                    origin_position=cache_entry.identifier_position,
                )

    async def get_type_document_symbols(self, uri: str) -> AsyncGenerator[BaseType]:
        """
        Gets a list of all types that are defined in the given document.
        """
        await self.validated_event.wait()
        for type_def in self.type_def_cache[unquote(uri)]:
            if not isinstance(type_def, Function) or not type_def.anonymous:
                yield type_def

    async def get_all_document_symbols(self, uri: str) -> list[BaseType | Namespace]:
        """
        Gets a full nested list of all namespaces, types and fields in the given document.
        """
        await self.validated_event.wait()
        return self.ast_cache[unquote(uri)]

    async def get_all_completion_type_defs(self, uri: str) -> list[BaseExternalType]:
        """
        a list of all known type_defs except of error types and anonymous function types
        """
        await self.validated_event.wait()
        return [
            type_def
            for type_def in self.generate_context[uri].resolver.registry.values()
            if (not isinstance(type_def, Function) or not type_def.anonymous) and not isinstance(type_def, ErrorDomain)
        ]

    async def get_all_error_domains(self, uri: str) -> list[ErrorDomain]:
        await self.validated_event.wait()
        return [
            type_def
            for type_def in self.generate_context[uri].resolver.registry.values()
            if isinstance(type_def, ErrorDomain)
        ]
    
    def get_all_target_languages(self) -> list[Target]:
        return [value for value in self.api.generation_targets.values() if not value.internal]

    async def generate_on_save(self, document: TextDocumentPath):
        await self.validated_event.wait()
        if self.configuration.generate_on_save and self.generate_context:
            generate_context = self.generate_context[document.as_uri()]
            for target in self.configured_context.configured_targets:
                generate_context.generate(target.key, clean=True)

    async def get_generated_sources(self, uri: str) -> AsyncGenerator[GeneratedSource]:
        await self.validated_event.wait()
        for target in self.configured_context.configured_targets:
            main_generator = next(generator for generator in target.generator_instances if generator.key == target.key)
            for type_def in self.type_def_cache[unquote(uri)]:
                if not isinstance(type_def, Function) or not type_def.anonymous:
                    if hasattr(type_def, target.key) and type_def.position:
                        target_type = getattr(type_def, target.key)
                        if hasattr(target_type, "header"):
                            file_output_path: Path = self.root_path / main_generator.header_path / target_type.header
                        else:
                            file_output_path: Path = self.root_path / main_generator.source_path / target_type.source
                        if file_output_path.exists():
                            yield GeneratedSource(
                                language=target.display_key,
                                uri=file_output_path.as_uri(),
                                type_def=type_def,
                            )


class LanguageServerAPI:
    def __init__(self):
        self.workspaces: list[Workspace] = []

    def add_workspace(self, uri: str) -> Workspace:
        workspace = Workspace(uri)
        self.workspaces.append(workspace)
        return workspace

    def get_workspace(self, uri: str) -> Workspace:
        for cache in self.workspaces:
            if unquote(uri).startswith(cache.root_uri):
                return cache
        raise ValueError(f"No cache found for URI: {uri}")

    def remove_workspace(self, uri: str) -> Workspace | None:
        for workspace in self.workspaces:
            if unquote(uri) == workspace.root_uri:
                self.workspaces.remove(workspace)
                return workspace
