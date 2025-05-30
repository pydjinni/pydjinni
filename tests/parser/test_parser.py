# Copyright 2023 - 2025 jothepro
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
import uuid
from pathlib import Path
from typing import TypeVar
from unittest.mock import MagicMock

import pytest

from pydjinni.exceptions import FileNotFoundException, ApplicationExceptionList
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFiles
from pydjinni.parser.ast import Record
from pydjinni.parser.base_models import BaseType, BaseExternalType, DataField
from pydjinni.parser.parser import Parser
from pydjinni.parser.resolver import Resolver


def given_mocks() -> tuple[FileReaderWriter, MagicMock]:
    reader = FileReaderWriter(Path.cwd())
    reader.setup(ProcessedFiles)
    return reader, MagicMock(spec=Resolver)


def given(tmp_path: Path, input_idl: str) -> tuple[Parser, MagicMock]:
    """
    Prepares the testing environment by initializing the parser and the file to be parsed.

    Args:
        tmp_path: path where the temporary IDL file should be written to
        input_idl: content of the IDL file that should be parsed

    Returns:
        instance of the Parser and the Path where the temporary IDL file can be found.
    """
    reader, resolver_mock = given_mocks()

    # GIVEN an input file
    input_file = tmp_path / f"{uuid.uuid4()}.pydjinni"
    input_file.write_text(input_idl)

    # AND GIVEN a Parser instance
    parser = Parser(
        resolver=resolver_mock,
        file_reader=reader,
        targets=[],
        supported_target_keys=["cpp", "java"],
        include_dirs=[tmp_path],
        default_deriving=set(),
        idl=input_file,
    )

    return parser, resolver_mock


TypeDef = TypeVar("TypeDef", bound=BaseType)


def when(parser: Parser, type_type: type[TypeDef], type_name: str = None) -> TypeDef:
    """
    parses the given input and asserts that the result is an AST with exactly one element
    of the expected type and name.

    Args:
        parser: parser to use for parsing
        input_file: IDL file to read
        type_type: the expected type of the resulting element in the AST
        type_name: the expected name of the resulting element in the AST

    Returns:
        the one element in the AST that was returned by the parser
    """
    # WHEN parsing the input file
    ast, _, _, _, _ = parser.parse()

    # THEN the resulting AST should contain one element
    assert len(ast) == 1

    # THEN the resulting AST should contain an enum object representing the input
    type_def = ast[0]
    assert isinstance(type_def, type_type)
    assert type_def.name == type_name
    return type_def


def assert_exception(parser: Parser, description: str):
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert exception.description == description


def assert_field(field: DataField, name: str, typename: str, optional: bool = False):
    assert field.name == name
    assert field.type_ref.name == typename
    assert field.type_ref.optional == optional


def test_parsing_invalid_input(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="****",
    )

    # WHEN parsing the input
    # THEN a IdlParser.ParsingException should be raised
    with pytest.raises(ApplicationExceptionList) as exception_info:
        parser.parse()
    assert len(exception_info.value.items) == 4
    for item in exception_info.value.items:
        assert isinstance(item, Parser.ParsingException)


def test_parsing_non_existing_file(tmp_path: Path):
    parser, _ = given(tmp_path=tmp_path, input_idl="")
    parser.idl = tmp_path / "test.djinni"

    # WHEN parsing a file that does not exist
    # THEN a FileNotFoundException should be raised
    with pytest.raises(FileNotFoundException):
        parser.parse()


def test_import(tmp_path: Path):
    # GIVEN an idl file that imports another file
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
                @import "foo.pydjinni"
                """,
    )
    # AND GIVEN the imported file
    imported_file = tmp_path / "foo.pydjinni"
    imported_file.write_text(
        """
    foo = record {
        bar: i8;
    }
    """
    )

    # THEN the record from the imported file should be included in the AST
    record = when(parser, Record, "foo")

    fields = record.fields
    assert len(fields) == 1
    assert_field(fields[0], name="bar", typename="i8")


def test_missing_import(tmp_path: Path):
    # GIVEN an idl file that imports another idl file that does not exist
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            @import "foo.pydjinni"
            """,
    )
    # WHEN parsing the file
    # THEN a FileNotFoundException should be raised
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, FileNotFoundException)


def test_detect_direct_recursive_import(tmp_path: Path):
    reader, resolver_mock = given_mocks()

    # GIVEN an input file
    filename = f"{uuid.uuid4()}.pydjinni"
    input_file = tmp_path / filename
    input_file.write_text(
        f"""
        @import "{filename}"
        """
    )

    # AND GIVEN a Parser instance
    parser = Parser(
        resolver=resolver_mock,
        file_reader=reader,
        targets=[],
        supported_target_keys=["cpp", "java"],
        include_dirs=[tmp_path],
        default_deriving=set(),
        idl=input_file,
    )

    # WHEN parsing the input
    # THEN a recursive input should be detected
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert exception.description == f"Circular import detected: file {input_file} directly references itself!"


def test_detect_indirect_recursive_import(tmp_path: Path):
    reader, resolver_mock = given_mocks()
    # GIVEN an input file
    filename = f"{uuid.uuid4()}.pydjinni"
    second_filename = f"{uuid.uuid4()}.pydjinni"
    input_file = tmp_path / filename
    second_file = tmp_path / second_filename
    input_file.write_text(
        f"""
        @import "{second_filename}"
        """
    )
    second_file.write_text(
        f"""
        @import "{filename}"
        """
    )

    # AND GIVEN a Parser instance
    parser = Parser(
        resolver=resolver_mock,
        file_reader=reader,
        targets=[],
        supported_target_keys=["cpp", "java"],
        include_dirs=[tmp_path],
        default_deriving=set(),
        idl=input_file,
    )

    # WHEN parsing the input
    # THEN a recursive input should be detected
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert "Circular import detected" in exception.description


def test_extern(tmp_path: Path):
    # GIVEN an idl file that references an extern type
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
        @extern "extern.yaml"
        """,
    )

    # AND GIVEN the extern file
    extern_file = tmp_path / "extern.yaml"
    extern_file.touch()

    # WHEN parsing the file
    ast, _, _, _, _ = parser.parse()

    # THEN the Resolver should have been called in order to load the external type
    resolver_mock.load_external.assert_called_once()
    resolver_mock.load_external.assert_called_with(extern_file)

    # THEN the resulting AST should be empty
    assert len(ast) == 0


def test_missing_extern(tmp_path: Path):
    # GIVEN an idl file that references an extern type that does not exist
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            @extern "extern.yaml"
            """,
    )

    # WHEN parsing the file
    # THEN a FileNotFoundException should be raised
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, FileNotFoundException)
    assert exception.description == Path("extern.yaml").absolute().as_uri()


def test_namespace(tmp_path: Path):
    # GIVEN an idl file that defines namespaces
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        namespace foo.bar {
            foo = enum {
                first_item;
                second_item;
            }
            namespace baz {
                bar = enum {
                    first_item;
                    second_item;
                }
            }
        }
        """,
    )

    # WHEN parsing the idl file
    defs, _, _, _, ast = parser.parse()

    # THEN the type_defs should contain two types each labelled with their respective namespace
    assert len(defs) == 2
    assert defs[0].name == "foo"
    assert defs[0].namespace == ["foo", "bar"]
    assert defs[1].name == "bar"
    assert defs[1].namespace == ["foo", "bar", "baz"]

    # THEN the ast should contain two nested namespaces
    assert len(ast) == 1
    assert ast[0].name == "foo.bar"
    assert len(ast[0].children) == 2
    assert ast[0].children[1].name == "baz"


def test_generic_parameters_not_allowed(tmp_path: Path):
    # GIVEN an idl file with a generic type reference
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = record {
                a: i8<i32>;
            }
                """,
    )

    # AND GIVEN a type that does not allow generic parameters
    resolver_mock.resolve.return_value = BaseExternalType(name="i8")

    # WHEN parsing the idl file
    # THEN an exception should be raised because of the unexpected generic parameter
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert exception.description == "Type 'i8' does not accept generic parameters"


def test_generic_parameters_invalid_number(tmp_path: Path):
    # GIVEN an idl file with a generic type reference
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = record {
                a: list<i32, i8>;
            }
                """,
    )

    # AND GIVEN a type that does not allow generic parameters
    resolver_mock.resolve.return_value = BaseExternalType(name="list", params=["T"])

    # WHEN parsing the idl file
    # THEN an exception should be raised because of the number of generic parameters is not correct
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert (
        exception.description
        == "Invalid number of generic parameters given to 'list'. Expects 1 (T), but 2 where given."
    )


def test_multiple_errors(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = record {
            a: i8
        }
        
        # @deprecated
        bar = interface {
        """,
    )

    # THEN an exception list should be raised
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 2
    first_exception = excinfo.value.items[0]
    assert isinstance(first_exception, Parser.ParsingException)
    assert first_exception.description.startswith("missing ';' at '}'")

    second_exception = excinfo.value.items[1]
    assert isinstance(second_exception, Parser.ParsingException)
    assert second_exception.description.startswith("mismatched input")

    # THEN despite the errors, a syntax tree should be included in the exception list
    assert len(excinfo.value.type_defs) == 2
    foo_type = excinfo.value.type_defs[0]
    assert foo_type.name == "foo"
    assert len(foo_type.fields) == 1
    assert foo_type.fields[0].name == "a"

    bar_type = excinfo.value.type_defs[1]
    assert bar_type.name == "bar"
    assert bar_type.deprecated
