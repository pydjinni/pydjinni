from pathlib import Path
from textwrap import dedent
from typing import Final, cast, get_type_hints
from unittest.mock import Mock

import pytest

from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.parser.factories.named_element_factory import NamedElementFactory
from pydjinni.parser.idl_parser import IdlParserImpl
from pydjinni.parser.model.elements import ResolvedFileReference
from pydjinni.parser.processing.parsetree_processor import ParsetreeProcessor


@pytest.fixture
def named_element_factory_mock() -> Mock:
    mock = Mock(NamedElementFactory)
    for method_name, method in NamedElementFactory.__dict__.items():
        if method_name.startswith("create_"):
            constructor = get_type_hints(method)["return"]
            getattr(mock, method_name).side_effect = constructor
    return mock


@pytest.fixture
def idl_parser(request: pytest.FixtureRequest, named_element_factory_mock: Mock, tmp_path: Path) -> IdlParserImpl:
    marker: Final = request.node.get_closest_marker("parser_input")
    assert marker is not None, "@pytest.mark.parser_input required"
    content: Final = marker.args[0]
    assert isinstance(content, str), "content parameter must be a string"

    path = Path("input.pydjinni")
    absolute_path = tmp_path / path
    absolute_path.touch()

    file_reader_writer_mock = Mock(FileReaderWriter)
    file_reader_writer_mock.read_idl.return_value = dedent(content)

    return IdlParserImpl(
        processor=ParsetreeProcessor(()),
        default_deriving=frozenset(),
        file_reader=file_reader_writer_mock,
        named_element_factory=cast(NamedElementFactory, named_element_factory_mock),
        file_reference=ResolvedFileReference(path=path, resolved_path=absolute_path),
    )
