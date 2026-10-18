from typing import Final
from unittest.mock import Mock
lazy from pathlib import Path

import pytest
from dirty_equals import HasAttributes, IsInstance, IsTuple

from pydjinni.parser.factories.idl_parser_factory import IdlParserFactory
from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import Interface, Record, ResolvedFileReference
from pydjinni.parser.providers.type_registry import TypeRegistry
from pydjinni.parser.yaml.yaml_type_parser import YamlTypeParser


@pytest.mark.parser_input(
    """
    foo = record {}

    bar = host interface {
        static foo() -> bar;
    }
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

    # GIVEN an IdlParserFactory
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

    # WHEN parsing some input
    parse_result = parser.parse()

    file_reader_writer_mock.read_idl.assert_called_once_with(idl_file)

    # THEN all elements of the input should be contained in the output
    assert parse_result.elements == IsTuple(
        IsInstance(Record),
        IsInstance(Interface)
        & HasAttributes(
            methods=IsTuple(IsInstance(Interface.Method)),
        ),
    )
    # AND THEN all processing rules should be applied and potential errors should be reported
    assert parse_result.diagnostics == IsTuple(
        IsInstance(Diagnostic) & HasAttributes(description="static methods are only allowed on native interfaces")
    )
