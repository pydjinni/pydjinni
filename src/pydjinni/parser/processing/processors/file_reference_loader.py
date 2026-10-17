from typing import Final, override
lazy from collections.abc import Iterable
lazy from pathlib import Path

from more_itertools import first, unique_everseen

from pydjinni.exceptions import ApplicationException
from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import ExternTypeReference, FileReference, ImportReference, ResolvedFileReference
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
lazy from pydjinni.parser.factories.parser_factory import ParserFactory
lazy from pydjinni.parser.providers.type_registry import TypeRegistry
lazy from pydjinni.parser.yaml.yaml_type_parser import YamlTypeParser
lazy from pydjinni.position import Position


class FileReferenceLoader(Processor[ExternTypeReference | ImportReference]):
    def __init__(
        self,
        yaml_type_parser: YamlTypeParser,
        type_registry: TypeRegistry,
        parser_factory: ParserFactory,
        include_dirs: tuple[Path, ...],
    ) -> None:
        self._yaml_type_parser: Final = yaml_type_parser
        self._type_registry: Final = type_registry
        self._parser_factory: Final = parser_factory
        self._include_dirs: Final = include_dirs

    @override
    def process(self, element: ExternTypeReference | ImportReference) -> ParseResult:
        try:
            resolved_file_reference: Final = self._resolve_file_reference(element.file_reference)
            if isinstance(element, ExternTypeReference):
                return ParseResult.from_parse_diagnostics(
                    *self._load_extern_type_reference(element.position, resolved_file_reference),
                )
            else:
                return self._load_import_reference(resolved_file_reference)
        except StopIteration:
            return ParseResult.from_parse_diagnostics(
                Diagnostic(
                    position=element.file_reference.position,
                    description=f"File not found: '{element.file_reference.path}'",
                    severity=Diagnostic.Severity.error,
                )
            )

    def _load_extern_type_reference(
        self, position: Position | None, file_reference: ResolvedFileReference
    ) -> Iterable[Diagnostic]:
        try:
            extern_types: Final = self._yaml_type_parser.parse(file_reference.resolved_path)
            for extern_type in extern_types:
                self._type_registry.register(extern_type)
        except ApplicationException as e:
            yield Diagnostic(
                position=position,
                description="Parsing the external type definition has failed",
                severity=Diagnostic.Severity.error,
                related_information=(
                    Diagnostic.RelatedInformation(
                        position=e.position,
                        description=e.description,
                    ),
                ),
            )

    def _load_import_reference(self, file_reference: ResolvedFileReference) -> ParseResult:
        if circular_import_chain := file_reference.circular_import_chain:
            return ParseResult.from_parse_diagnostics(
                Diagnostic(
                    position=first(circular_import_chain).position,
                    description=f"Circular import detected: {' -> '.join(f"'{file_reference.path}'" for file_reference in circular_import_chain)}",
                    severity=Diagnostic.Severity.error,
                )
            )
        else:
            return self._parser_factory.create_parser(file_reference).parse()

    def _resolve_file_reference(self, file_reference: FileReference) -> ResolvedFileReference:
        """
        Raises:
            StopIteration: If no matching file could be found to resolve the FileReference
        """
        if file_reference.path.is_absolute() and file_reference.path.is_file():
            resolved_path = file_reference.path
        else:
            if file_reference.parent:
                working_directory: Final = file_reference.parent.resolved_path.parent
                all_include_dirs = unique_everseen((working_directory, *self._include_dirs))
            else:
                all_include_dirs = self._include_dirs
            search_dirs: Final = ((include_dir / file_reference.path) for include_dir in all_include_dirs)
            resolved_path = next(search_dir for search_dir in search_dirs if search_dir.is_file())
        return ResolvedFileReference(
            position=file_reference.position,
            namespace=file_reference.namespace,
            path=file_reference.path,
            parent=file_reference.parent,
            resolved_path=resolved_path,
        )
