from pathlib import Path
from typing import cast
from unittest.mock import Mock

import pytest
from more_itertools import one

from pydjinni.exceptions import InputParsingException
from pydjinni.parser.factories.idl_parser_factory import IdlParserFactory
from pydjinni.parser.idl_parser import IdlParserImpl
from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import (
    ExternTypeReference,
    FileReference,
    ImportReference,
    ResolvedFileReference,
    Type,
)
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.processors.file_reference_loader import FileReferenceLoader
from pydjinni.parser.yaml.yaml_type_parser import YamlTypeParser
from pydjinni.position import Position
lazy from pydjinni.parser.providers.type_registry import TypeRegistry


@pytest.fixture
def yaml_type_parser_mock() -> Mock:
    return Mock(YamlTypeParser)


@pytest.fixture
def parser_factory_mock() -> Mock:
    return Mock(IdlParserFactory)


@pytest.fixture
def file_reference_loader(
    yaml_type_parser_mock: Mock,
    type_registry_mock: Mock,
    parser_factory_mock: Mock,
) -> FileReferenceLoader:
    return FileReferenceLoader(
        yaml_type_parser=cast("YamlTypeParser", yaml_type_parser_mock),
        type_registry=cast("TypeRegistry", type_registry_mock),
        parser_factory=cast("IdlParserFactory", parser_factory_mock),
        include_dirs=(),
    )


def test_extern_type_reference_file_not_found(file_reference_loader: FileReferenceLoader):
    # GIVEN an ExternTypeReference to a file that can not be resolved
    file_position = Mock(Position)
    extern_type_reference = ExternTypeReference(
        file_reference=FileReference(
            position=file_position,
            path=Path("foo.yaml"),
        ),
    )

    # WHEN processing the ExternTypeReference
    parse_result = file_reference_loader.process(extern_type_reference)

    # THEN a ParseIssue should be returned, because the file could not be found
    assert one(parse_result.diagnostics) == Diagnostic(
        position=file_position,
        description="File not found: 'foo.yaml'",
        severity=Diagnostic.Severity.error,
    )


def test_extern_file_parsing_issue(
    tmp_path: Path,
    yaml_type_parser_mock: Mock,
    file_reference_loader: FileReferenceLoader,
):
    # GIVEN a successfully resolved ExternTypeReference
    current_file_path = Path("foo.pydjinni")
    import_position = Position.from_file(file=tmp_path / current_file_path)
    extern_type_file_path = Path("foo.yaml")
    resolved_extern_type_file_path = tmp_path / extern_type_file_path
    resolved_extern_type_file_path.touch()
    extern_type_reference = ExternTypeReference(
        position=import_position,
        file_reference=FileReference(
            path=extern_type_file_path,
            parent=ResolvedFileReference(
                path=current_file_path,
                resolved_path=tmp_path / current_file_path,
            ),
        ),
    )

    yaml_parsing_exception_position = Mock(Position)
    yaml_type_parser_mock.parse.side_effect = InputParsingException(
        position=yaml_parsing_exception_position,
        description="something went wrong",
    )

    # WHEN processing the ExternTypeReference
    parse_result = file_reference_loader.process(extern_type_reference)

    # THEN a ParseIssue should be returned, because the file could not be found
    assert one(parse_result.diagnostics) == Diagnostic(
        position=import_position,
        description="Parsing the external type definition has failed",
        severity=Diagnostic.Severity.error,
        related_information=(
            Diagnostic.RelatedInformation(
                position=yaml_parsing_exception_position,
                description="something went wrong",
            ),
        ),
    )


def test_extern_file_parsing_success(
    tmp_path: Path,
    yaml_type_parser_mock: Mock,
    type_registry_mock: Mock,
    file_reference_loader: FileReferenceLoader,
):
    # GIVEN a successfully resolved ExternTypeReference
    current_file_path = Path("foo.pydjinni")
    import_position = Mock(Position)
    extern_type_file_path = Path("foo.yaml")
    resolved_extern_type_file_path = tmp_path / extern_type_file_path
    resolved_extern_type_file_path.touch()
    extern_type_reference = ExternTypeReference(
        position=import_position,
        file_reference=FileReference(
            path=extern_type_file_path,
            parent=ResolvedFileReference(
                path=current_file_path,
                resolved_path=tmp_path / current_file_path,
            ),
        ),
    )

    # AND GIVEN a YamlTypeParser that returns two types on parse
    yaml_type_parser_mock.parse.return_value = (Mock(Type), Mock(Type))

    # WHEN processing the ExternTypeReference
    parse_result = file_reference_loader.process(extern_type_reference)

    # THEN no ParseIssue should be returned
    assert len(parse_result.diagnostics) == 0

    # THEN the YamlTypeParser should be called for parsing the file
    yaml_type_parser_mock.parse.assert_called_once_with(resolved_extern_type_file_path)

    # THEN the new types should be registered at the TypeRegistry
    assert type_registry_mock.register.call_count == 2


def test_import_reference_not_found(
    parser_factory_mock: Mock,
    file_reference_loader: FileReferenceLoader,
):
    import_position = Mock(Position)
    import_path = Path("foo.yaml")
    # GIVEN a ImportReference that has no resolved path
    import_reference = ImportReference(
        file_reference=FileReference(
            position=import_position,
            path=import_path,
        )
    )

    # WHEN processing the ImportReference
    parse_result = file_reference_loader.process(import_reference)

    # THEN a ParseIssue should be returned, because the file was not found
    assert one(parse_result.diagnostics) == Diagnostic(
        position=import_position,
        description=f"File not found: '{import_path}'",
        severity=Diagnostic.Severity.error,
    )

    # THEN the ParserFactory should not be called
    parser_factory_mock.create_parser.assert_not_called()


def test_import_reference_circular_import(
    tmp_path: Path,
    parser_factory_mock: Mock,
    file_reference_loader: FileReferenceLoader,
):
    # GIVEN an ImportReference with a circular FileReference chain
    first_import_path = Path("a.pydjinni")
    first_resolved_path = tmp_path / first_import_path
    first_file_reference = ResolvedFileReference(
        path=first_import_path,
        resolved_path=first_resolved_path,
    )
    first_resolved_path.touch()

    second_import_path = Path("b.pydjinni")
    second_resolved_path = tmp_path / second_import_path
    second_file_position = Position.from_file(first_resolved_path)
    second_file_reference = ResolvedFileReference(
        position=second_file_position,
        path=second_import_path,
        resolved_path=second_resolved_path,
        parent=first_file_reference,
    )
    second_resolved_path.touch()

    third_file_reference = FileReference(
        position=Position.from_file(second_resolved_path),
        path=first_import_path,
        parent=second_file_reference,
    )

    import_reference = ImportReference(file_reference=third_file_reference)

    # WHEN processing the ImportReference
    parse_result = file_reference_loader.process(import_reference)

    # THEN a ParseIssue should be returned for the circular import
    assert one(parse_result.diagnostics) == Diagnostic(
        position=second_file_position,
        description="Circular import detected: 'b.pydjinni' -> 'a.pydjinni'",
        severity=Diagnostic.Severity.error,
    )

    # THEN the ParserFactory should not be called
    parser_factory_mock.create_parser.assert_not_called()


def test_valid_import_reference(
    tmp_path: Path,
    parser_factory_mock: Mock,
    file_reference_loader: FileReferenceLoader,
):
    # GIVEN a valid ImportReference
    current_file_path = Path("a.pydjinni")
    current_file_reference = ResolvedFileReference(
        path=current_file_path,
        resolved_path=tmp_path / current_file_path,
    )
    imported_file_path = Path("b.pydjinni")
    resolved_imported_file_path = tmp_path / imported_file_path
    resolved_imported_file_path.touch()
    import_reference = ImportReference(
        file_reference=FileReference(
            path=imported_file_path,
            parent=current_file_reference,
        )
    )

    imported_parser = Mock(IdlParserImpl)
    imported_parse_result = Mock(ParseResult)
    imported_parser.parse.return_value = imported_parse_result
    parser_factory_mock.create_parser.return_value = imported_parser

    # WHEN processing the ImportReference
    parse_result = file_reference_loader.process(import_reference)

    # THEN the ParserFactory should be called
    parser_factory_mock.create_parser.assert_called_once_with(
        ResolvedFileReference(
            path=imported_file_path,
            resolved_path=resolved_imported_file_path,
            parent=current_file_reference,
        )
    )

    # AND THEN the parsing should be triggered
    imported_parser.parse.assert_called_once()

    # AND THEN the ParseResult should be returned
    assert parse_result is imported_parse_result
