import uuid
from pathlib import Path
from typing import TypeVar
from unittest.mock import MagicMock

import pytest

from pydjinni.exceptions import FileNotFoundException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFiles
from pydjinni.generator.target import Target
from pydjinni.parser.ast import Record, Enum, Flags, Interface, TypeReference, Function
from pydjinni.parser.base_models import BaseType, BaseExternalType, Position
from pydjinni.parser.parser import IdlParser
from pydjinni.parser.resolver import Resolver


def given(tmp_path: Path, input_idl: str) -> tuple[IdlParser, MagicMock]:
    """
    Prepares the testing environment by initializing the parser and the file to be parsed.

    Args:
        tmp_path: path where the temporary IDL file should be written to
        input_idl: content of the IDL file that should be parsed

    Returns:
        instance of the Parser and the Path where the temporary IDL file can be found.
    """
    reader = FileReaderWriter()
    reader.setup(ProcessedFiles)
    resolver_mock = MagicMock(spec=Resolver)

    # AND GIVEN an input file
    input_file = tmp_path / f"{uuid.uuid4()}.djinni"
    input_file.write_text(input_idl)

    # GIVEN a Parser instance
    parser = IdlParser(
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


def when(parser: IdlParser, type_type: type[TypeDef], type_name: str = None) -> TypeDef:
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
            const foobar: i8 = 5;
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

    # THEN the record should have the defined constant
    assert len(record.constants) == 1
    constant = record.constants[0]
    assert constant.name == "foobar"
    assert constant.type_ref.name == "i8"
    assert constant.value == 5
    assert type(constant.value) is int


@pytest.mark.parametrize("deriving,expected", [
    ('eq', {Record.Deriving.eq}),
    ('eq, ord', {Record.Deriving.eq, Record.Deriving.ord}),
    ('eq, ord, str', {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str}),
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
                const b: i8 = 5;
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

    # then the defined constants should be present
    assert len(interface.constants) == 1
    constant = interface.constants[0]
    assert constant.name == "b"
    assert constant.value == 5
    assert constant.type_ref.name == "i8"

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
    with pytest.raises(IdlParser.ParsingException, match="Unknown interface target 'foo'"):
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
    with pytest.raises(IdlParser.ParsingException, match="methods are only allowed to be static on 'cpp' interfaces"):
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
    with pytest.raises(IdlParser.ParsingException, match="method cannot be both static and const"):
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
    with pytest.raises(IdlParser.ParsingException):
        parser.parse()


def test_parsing_function(tmp_path):
    # GIVEN a named function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="foo = function (param: i8) -> bool;"
    )

    function = when(parser, Function, "foo")

    # THEN the function should have the expected parameters and return type
    assert len(function.parameters) == 1
    assert function.parameters[0].name == "param"
    assert function.parameters[0].type_ref.name == "i8"
    assert function.return_type_ref.name == "bool"


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


@pytest.mark.parametrize("input", [
    """
    foo = record {
        field: ();
    }
    """,
    """
    foo = record {
        const field: () = 0;
    }""",
    """
    foo = interface {
        const field: () = 0;
    }
    """
])
def test_parsing_anonymous_function_not_allowed(tmp_path: Path, input):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=input
    )

    # WHEN parsing the input
    # THEN a ParsingException should be raised because functions are not allowed in the given context
    with pytest.raises(IdlParser.ParsingException, match="functions are not allowed"):
        parser.parse()

def test_parsing_invalid_input(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="****",
    )

    # WHEN parsing the input
    # THEN a IdlParser.ParsingException should be raised
    with pytest.raises(IdlParser.ParsingException):
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


@pytest.mark.parametrize("typename,primitive,literal_value,value", [
    ('i8', BaseExternalType.Primitive.int, '5', 5),
    ('f32', BaseExternalType.Primitive.float, '42.2', 42.2),
    ('bool', BaseExternalType.Primitive.bool, 'True', True),
    ('bool', BaseExternalType.Primitive.bool, 'False', False),
    ('string', BaseExternalType.Primitive.string, '"the foo is in the bar"', "the foo is in the bar"),
])
def test_record_primitive_constant(tmp_path, typename, primitive, literal_value, value):
    # GIVEN an idl file that defines a record with a constant
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl=f"""
        foo = record {{
            const bar: {typename} = {literal_value};
        }}
        """
    )

    # AND GIVEN a resolver that returns the matching primitive type
    resolver_mock.resolve.return_value = BaseExternalType(
            name=typename,
            primitive=primitive
        )

    record = when(parser, Record, "foo")

    # THEN the record should contain the defined constant and value
    assert len(record.constants) == 1
    constant = record.constants[0]
    assert constant.name == "bar"
    assert constant.value == value
    assert constant.type_ref.name == typename


@pytest.mark.parametrize("typename,primitive,literal_value", [
    ('i8', BaseExternalType.Primitive.int, '"this is a number, I swear!"'),
    ('i8', BaseExternalType.Primitive.int, '52.6'),
    ('i8', BaseExternalType.Primitive.int, 'True'),
    ('i8', BaseExternalType.Primitive.int, 'False'),
    ('f32', BaseExternalType.Primitive.float, '42'),
    ('f32', BaseExternalType.Primitive.float, '"42"'),
    ('f32', BaseExternalType.Primitive.float, 'True'),
    ('f32', BaseExternalType.Primitive.float, 'False'),
    ('bool', BaseExternalType.Primitive.bool, '"the truth is here"'),
    ('bool', BaseExternalType.Primitive.bool, '4'),
    ('bool', BaseExternalType.Primitive.bool, '4.2'),
    ('string', BaseExternalType.Primitive.string, '5'),
    ('string', BaseExternalType.Primitive.string, '5.4'),
    ('string', BaseExternalType.Primitive.string, 'True'),
    ('string', BaseExternalType.Primitive.string, 'False'),
])
def test_record_wrong_primitive_constant(tmp_path, typename, primitive, literal_value):
    # GIVEN an idl file that defines a record with a constant
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl=f"""
            foo = record {{
                const bar: {typename} = {literal_value};
            }}
            """
    )

    # AND GIVEN a resolver that returns a primitive type that does not match the provided const value
    resolver_mock.resolve.return_value = BaseExternalType(
            name=typename,
            primitive=primitive
        )

    # WHEN parsing the idl
    # THEN a Parsing exception should be thrown
    with pytest.raises(IdlParser.ParsingException):
        when(parser, Record, "foo")


@pytest.mark.parametrize("literal_value", [
    '5', '5.5', 'false', 'true', '"test"', '{a="foo"}', '{a=5.5}', '{a=true}'
])
def test_record_wrong_const_record_assignment(tmp_path, literal_value):
    # GIVEN an idl file that assigns a primitive value to a const record type
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl=f"""
                bar = record {{
                    const b: foo = {literal_value};
                }}
                """
    )

    resolver_mock.resolve.return_value = Record(
        name="foo",
        primitive=BaseExternalType.Primitive.record,
        fields=[
            Record.Field(
                name="a",
                type_ref=TypeReference(
                    name="i8",
                    type_def=BaseExternalType(
                        name="i8",
                        primitive=BaseExternalType.Primitive.int
                    )
                )
            )
        ],
        constants=[],
        targets=[],
        deriving=set()
    )

    # WHEN parsing the file
    # THEN a InvalidAssignmentException should be raised
    with pytest.raises(IdlParser.ParsingException, match="Invalid"):
        parser.parse()


def test_record_wrong_const_unknown_field_assignment(tmp_path):
    # GIVEN an idl file that assigns an object with an unknown field to a const value
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
                    bar = record {
                        const b: foo = {b=5};
                    }
                    """
    )

    resolver_mock.resolve.return_value = Record(
        name="foo",
        primitive=BaseExternalType.Primitive.record,
        fields=[
            Record.Field(
                name="a",
                type_ref=TypeReference(
                    name="i8",
                    type_def=BaseExternalType(
                        name="i8",
                        primitive=BaseExternalType.Primitive.int
                    )
                )
            )
        ],
        constants=[],
        targets=[],
        deriving=set()
    )

    # WHEN parsing the file
    # THEN a UnknownFieldException should be raised
    with pytest.raises(IdlParser.ParsingException, match="Unknown field 'b' defined in constant assignment"):
        parser.parse()
