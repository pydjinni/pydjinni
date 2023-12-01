# Copyright 2023 jothepro
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

from pydjinni.exceptions import FileNotFoundException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFiles
from pydjinni.parser.ast import Record, Enum, Flags, Interface, Function
from pydjinni.parser.base_models import BaseType
from pydjinni.parser.parser import Parser
from pydjinni.parser.resolver import Resolver


def given_mocks() -> tuple[FileReaderWriter, MagicMock]:
    reader = FileReaderWriter()
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
        idl=input_file
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
    ast = parser.parse()

    # THEN the resulting AST should contain one element
    assert len(ast) == 1

    # THEN the resulting AST should contain an enum object representing the input
    type_def = ast[0]
    assert isinstance(type_def, type_type)
    assert type_def.name == type_name
    return type_def


def test_parsing_enum(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = enum {
            first_item;
            second_item;
        }
        """
    )

    enum = when(parser, Enum, "foo")

    items = enum.items

    # THEN the resulting enum should have exactly two items
    assert len(items) == 2
    assert items[0].name == "first_item"
    assert items[1].name == "second_item"


def assert_flag(flag: Flags.Flag, name: str, none: bool = False, all: bool = False):
    """asserts that a flag has all attributes set as excepted"""
    assert flag.name == name
    assert flag.none == none
    assert flag.all == all


def test_parsing_flags(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = flags {
            flag1;
            flag2;
            no_flags = none;
            all_flags = all;
        }
        """
    )

    flags = when(parser, Flags, "foo")

    flag_items = flags.flags

    # THEN the resulting flags should have exactly 4 items
    assert len(flag_items) == 4
    assert_flag(flag_items[0], name="flag1")
    assert_flag(flag_items[1], name="flag2")
    assert_flag(flag_items[2], name="no_flags", none=True)
    assert_flag(flag_items[3], name="all_flags", all=True)


def assert_field(field: Record.Field, name: str, typename: str, optional: bool = False):
    assert field.name == name
    assert field.type_ref.name == typename
    assert field.type_ref.optional == optional


def test_parsing_record(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = record {
            bar: i8;
            baz: i8?;
        }
        """
    )

    record = when(parser, Record, "foo")

    fields = record.fields

    # THEN the record should have exactly 2 fields
    assert len(fields) == 2
    assert_field(fields[0], name="bar", typename="i8")
    assert_field(fields[1], name="baz", typename="i8", optional=True)
    assert not record.targets


@pytest.mark.parametrize("deriving,expected", [
    ('eq', {Record.Deriving.eq}),
    ('eq, ord', {Record.Deriving.eq, Record.Deriving.ord}),
    ('eq, ord, str', {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str}),
    ('eq, eq', {Record.Deriving.eq})
])
def test_parsing_record_deriving(tmp_path: Path, deriving, expected: set[Record.Deriving]):
    # GIVEN an idl file that defines a record that derives some extensions
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
            foo = record {{
                baz: i8;
            }} deriving ({deriving})
            """
    )

    record = when(parser, Record, "foo")

    # THEN only the derived extensions should be enabled
    assert record.deriving == expected


def test_parsing_record_unknown_deriving(tmp_path: Path):
    # GIVEN an idl file that defines a record that derives an unknown extension
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
                foo = record {{}} deriving (loremipsum)
                """
    )

    # WHEN parsing the input
    # THEN an error should be raised
    with pytest.raises(Parser.ParsingException, match="'loremipsum' is not a valid record extension"):
        parser.parse()


@pytest.mark.parametrize("deriving,expected", [
    ('', {Record.Deriving.eq, Record.Deriving.ord}),
    ('deriving()', {Record.Deriving.eq, Record.Deriving.ord}),
    ('deriving(ord)', {Record.Deriving.eq, Record.Deriving.ord}),
    ('deriving(eq, ord, str)', {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str}),
])
def test_parsing_record_default_deriving(tmp_path: Path, deriving, expected: set[Record.Deriving]):
    reader, resolver_mock = given_mocks()

    # GIVEN an input file
    input_file = tmp_path / f"{uuid.uuid4()}.pydjinni"
    input_file.write_text(f"""
    foo = record {{}} {deriving}
    """)

    # AND GIVEN a Parser instance with a set of default deriving extensions
    parser = Parser(
        resolver=resolver_mock,
        file_reader=reader,
        targets=[],
        supported_target_keys=["cpp", "java"],
        include_dirs=[tmp_path],
        default_deriving={Record.Deriving.eq, Record.Deriving.ord},
        idl=input_file
    )

    # WHEN parsing the input
    # THEN the record should contain the defined default extensions
    record = when(parser, Record, "foo")
    assert record.deriving == expected


def test_parsing_base_record(tmp_path: Path):
    # GIVEN an idl file that defines a record will be extended in C++
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
                foo = record +cpp {
                    baz: i8;
                }
                """
    )
    record = when(parser, Record, "foo")

    # THEN the target language C++ should be set
    assert len(record.targets) == 1
    assert 'cpp' in record.targets


def assert_method(method: Interface.Method, name: str, params: list[tuple[str, str]] = None, return_type: str = None,
                  static: bool = False, const: bool = False):
    assert method.name == name
    assert method.static == static
    assert method.const == const
    if return_type:
        assert method.return_type_ref.name == return_type
    else:
        assert method.return_type_ref is None
    if params:
        assert len(method.parameters) == len(params)
        for param in method.parameters:
            assert (param.name, param.type_ref.name) in params
    else:
        assert len(method.parameters) == 0


def test_parsing_interface(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +cpp {
                method();
                static static_method();
                const const_method();
                method_with_return() -> i8;
                method_with_parameter(param: i8);
                method_with_parameters_and_return(param: i8, param2: i8) -> i8;
                property a: i8;
            }
            """
    )

    interface = when(parser, Interface, "foo")

    methods = interface.methods

    # THEN the interface should not be marked as 'main'
    assert not interface.main

    # THEN the interface should have exactly 5 methods
    assert len(methods) == 6

    # THEN the methods should have the expected names, parameters and attributes
    assert_method(methods[0], "method")
    assert_method(methods[1], "static_method", static=True)
    assert_method(methods[2], "const_method", const=True)
    assert_method(methods[3], "method_with_return", return_type="i8")
    assert_method(methods[4], "method_with_parameter", params=[("param", "i8")])
    params = [("param", "i8"), ("param2", "i8")]
    assert_method(methods[5], "method_with_parameters_and_return", params=params, return_type="i8")

    # then the expected targets should be defined
    assert "cpp" in interface.targets
    assert len(interface.targets) == 1

    # then the defined properties should be present
    assert len(interface.properties) == 1
    property_def = interface.properties[0]
    assert property_def.name == "a"
    assert property_def.type_ref.name == "i8"


def test_parsing_interface_unknown_target(tmp_path: Path):
    # GIVEN an idl file that references an unknown target language for the defined interface
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +foo {
                method();
            }
            """
    )
    # WHEN parsing the input
    # THEN a IdlParser.UnknownInterfaceTargetException should be raised
    with pytest.raises(Parser.ParsingException, match="Unknown interface target 'foo'"):
        parser.parse()


def test_parsing_interface_no_target(tmp_path: Path):
    # GIVEN an idl file that references no target language for the defined interface
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface {
                method();
            }
            """
    )
    # WHEN parsing the input
    interface = when(parser, Interface, "foo")
    # THEN all known interface targets should be set for the defined interface
    assert "cpp" in interface.targets
    assert "java" in interface.targets
    assert len(interface.targets) == 2


def test_parsing_interface_minus_target(tmp_path: Path):
    # GIVEN an idl file that only references the exclusion of a target from the defined interface
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface -cpp {
                method();
            }
            """
    )
    # WHEN parsing the input
    interface = when(parser, Interface, "foo")
    # THEN all known interface targets except the one excluded should be present in the interface
    assert "java" in interface.targets
    assert len(interface.targets) == 1


def test_parsing_interface_static_not_allowed(tmp_path):
    # GIVEN an idl file that defines an interface with a static method that is not targeting `cpp`
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface -cpp {
                static foo();
            }       
            """
    )

    # THEN a StaticNotAllowedException should be raised
    with pytest.raises(Parser.ParsingException, match="methods are only allowed to be static on 'cpp' interfaces"):
        parser.parse()


def test_parsing_interface_static_and_const_not_allowed(tmp_path):
    # GIVEN an idl file that defines an interface with a static const method
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +cpp {
                static const foo();
            }       
            """
    )

    # THEN a StaticAndConstException should be raised
    with pytest.raises(Parser.ParsingException, match="method cannot be both static and const"):
        parser.parse()


def test_parsing_main_interface(tmp_path):
    # GIVEN an idl file that defines a main interface (code entrypoint)
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = main interface +cpp {}       
            """
    )
    # WHEN parsing the input
    interface = when(parser, Interface, "foo")

    # THEN the interface should be marked as 'main'
    assert interface.main


@pytest.mark.parametrize("targets", ["-cpp", "+cpp +java"])
def test_parsing_main_interface_not_cpp(tmp_path, targets):
    # GIVEN an idl file that defines a main interface (code entrypoint)
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
            foo = main interface {targets} {{}}       
            """
    )
    # WHEN parsing the input
    # THEN a ParsingException should be thrown because the 'main' interface is not implemented in C++
    with pytest.raises(Parser.ParsingException, match="a 'main' interface can only be implemented in C\+\+"):
        parser.parse()


def test_parsing_function(tmp_path):
    # GIVEN a named function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="foo = function +cpp (param: i8) -> bool;"
    )

    function = when(parser, Function, "foo")

    # THEN the function should have the expected parameters and return type
    assert len(function.parameters) == 1
    assert function.parameters[0].name == "param"
    assert function.parameters[0].type_ref.name == "i8"
    assert function.return_type_ref.name == "bool"
    # THEN all the specified language target should be set
    assert "cpp" in function.targets
    assert len(function.targets) == 1


def test_parsing_function_no_target(tmp_path: Path):
    # GIVEN a named function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="foo = function (param: i8) -> bool;"
    )

    function = when(parser, Function, "foo")

    # THEN all known language targets should be set for the defined interface
    assert "cpp" in function.targets
    assert "java" in function.targets
    assert len(function.targets) == 2

def test_parsing_function_minus_target(tmp_path: Path):
    # GIVEN a named function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="foo = function -cpp (param: i8) -> bool;"
    )

    function = when(parser, Function, "foo")

    # THEN all known language targets minus the one specified in the interface should be set for the defined interface
    assert "java" in function.targets
    assert len(function.targets) == 1

def test_parsing_inline_function(tmp_path):
    # GIVEN an interface with an inline function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = interface {
            method(callback: function (var: i8));
        }
        """
    )
    # WHEN parsing the input
    ast = parser.parse()

    # THEN the anonymous type should be registered in the output AST
    assert len(ast) == 2
    assert isinstance(ast[0], Function)
    assert isinstance(ast[1], Interface)

    # THEN the method should reference an anonymous (nameless) function
    interface: Interface = ast[1]
    function = interface.methods[0].parameters[0].type_ref.type_def
    assert isinstance(function, Function)
    assert function.parameters[0].name == "var"
    assert function.return_type_ref is None


def test_parsing_anonymous_function_not_allowed(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = record {
                field: ();
            }
            """
    )

    # WHEN parsing the input
    # THEN a ParsingException should be raised because functions are not allowed in records
    with pytest.raises(Parser.ParsingException, match="functions are not allowed"):
        parser.parse()


def test_parsing_invalid_input(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="****",
    )

    # WHEN parsing the input
    # THEN a IdlParser.ParsingException should be raised
    with pytest.raises(Parser.ParsingException):
        parser.parse()


def test_parsing_non_existing_file(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=""
    )
    parser.idl = tmp_path / 'test.djinni'

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
                """
    )
    # AND GIVEN the imported file
    imported_file = tmp_path / "foo.pydjinni"
    imported_file.write_text("""
    foo = record {
        bar: i8;
    }
    """)

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
                  """
    )
    # WHEN parsing the file
    # THEN a FileNotFoundException should be raised
    with pytest.raises(FileNotFoundException):
        parser.parse()


def test_detect_direct_recursive_import(tmp_path: Path):
    reader, resolver_mock = given_mocks()

    # GIVEN an input file
    filename = f"{uuid.uuid4()}.pydjinni"
    input_file = tmp_path / filename
    input_file.write_text(f"""
    @import "{filename}"
    """)

    # AND GIVEN a Parser instance
    parser = Parser(
        resolver=resolver_mock,
        file_reader=reader,
        targets=[],
        supported_target_keys=["cpp", "java"],
        include_dirs=[tmp_path],
        default_deriving=set(),
        idl=input_file
    )

    # WHEN parsing the input
    # THEN a recursive input should be detected
    with pytest.raises(Parser.ParsingException,
                       match=f"Circular import detected: file {input_file} directly references itself!"):
        parser.parse()


def test_detect_indirect_recursive_import(tmp_path: Path):
    reader, resolver_mock = given_mocks()
    # GIVEN an input file
    filename = f"{uuid.uuid4()}.pydjinni"
    second_filename = f"{uuid.uuid4()}.pydjinni"
    input_file = tmp_path / filename
    second_file = tmp_path / second_filename
    input_file.write_text(f"""
    @import "{second_filename}"
    """)
    second_file.write_text(f"""
    @import "{filename}"
    """)

    # AND GIVEN a Parser instance
    parser = Parser(
        resolver=resolver_mock,
        file_reader=reader,
        targets=[],
        supported_target_keys=["cpp", "java"],
        include_dirs=[tmp_path],
        default_deriving=set(),
        idl=input_file
    )

    # WHEN parsing the input
    # THEN a recursive input should be detected
    with pytest.raises(Parser.ParsingException, match=f"indirectly imports itself!"):
        parser.parse()


def test_extern(tmp_path: Path):
    # GIVEN an idl file that references an extern type
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
        @extern "extern.yaml"
        """
    )

    # AND GIVEN the extern file
    extern_file = tmp_path / "extern.yaml"
    extern_file.touch()

    # WHEN parsing the file
    ast = parser.parse()

    # THEN the Resolver should have been called in order to load the external type
    resolver_mock.load_external.assert_called_once()
    resolver_mock.load_external.assert_called_with(extern_file)

    # THEN the resulting AST should be empty
    assert len(ast) == 0


def test_missing_extern(tmp_path: Path):
    # GIVEN an idl file that references an extern type that does not exist
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            @extern "extern.yaml"
            """
    )

    # WHEN parsing the file
    # THEN a FileNotFoundException should be raised
    with pytest.raises(FileNotFoundException):
        parser.parse()


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
            """
    )

    # WHEN parsing the idl file
    ast = parser.parse()

    # THEN the ast should contain two types each labelled with their respective namespace
    assert len(ast) == 2
    assert ast[0].name == "foo"
    assert ast[0].namespace == ["foo", "bar"]
    assert ast[1].name == "bar"
    assert ast[1].namespace == ["foo", "bar", "baz"]
