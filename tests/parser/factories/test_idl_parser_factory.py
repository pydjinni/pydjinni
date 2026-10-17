from typing import Final
from unittest.mock import Mock
lazy from pathlib import Path

import pytest
from dirty_equals import IsInstance, IsTuple

from pydjinni.parser.factories.idl_parser_factory import IdlParserFactory
from pydjinni.parser.model.elements import Interface, Record, ResolvedFileReference
from pydjinni.parser.providers.type_registry import TypeRegistry
from pydjinni.parser.yaml.yaml_type_parser import YamlTypeParser


@pytest.mark.parser_input(
    """
    foo = record {}

    bar = interface {}
    """
)
def test_parser_factory(
    tmp_path: Path,
    named_element_factory_mock: Mock,
    file_reader_writer_mock: Mock,
):
    yaml_type_parser_mock: Final = Mock(YamlTypeParser)
    type_registry_mock: Final = Mock(TypeRegistry)
    include_dirs: Final = ()
    default_deriving: Final = frozenset[Record.Deriving]()

    parser_factory = IdlParserFactory(
        yaml_type_parser=yaml_type_parser_mock,
        type_registry=type_registry_mock,
        include_dirs=include_dirs,
        default_deriving=default_deriving,
        file_reader=file_reader_writer_mock,
        named_element_factory=named_element_factory_mock,
    )

    idl_file = tmp_path / "idl.pydjinni"

    parser = parser_factory.create_parser(ResolvedFileReference.from_absolute_path(idl_file))

    parse_result = parser.parse()

    assert parse_result.elements == IsTuple(IsInstance(Record), IsInstance(Interface))
    assert len(parse_result.diagnostics) == 0
