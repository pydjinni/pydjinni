import uuid
from pathlib import Path
from typing import TypeVar
from unittest.mock import MagicMock

import pytest

from pydjinni.exceptions import FileNotFoundException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFiles
from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Record, Enum, Flags, Interface, TypeReference
from pydjinni.parser.base_models import BaseType, BaseField, BaseExternalType
from pydjinni.parser.parser import IdlParser
from pydjinni.parser.resolver import Resolver


def given(tmp_path: Path, input_idl: str) -> tuple[IdlParser, MagicMock, MagicMock]:
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
    marshal_mock = MagicMock(spec=Marshal)

    # AND GIVEN an input file
    input_file = tmp_path / f"{uuid.uuid4()}.djinni"
    input_file.write_text(input_idl)

    # GIVEN a Parser instance
    parser = IdlParser(
        resolver=resolver_mock,
        marshals=[marshal_mock],
        file_reader=reader,
        targets=['cpp', 'java'],
        include_dirs=[tmp_path],
        idl=input_file
    )

    return parser, resolver_mock, marshal_mock


TypeDef = TypeVar("TypeDef", bound=BaseType)


def when(parser: IdlParser, type_type: type[TypeDef], type_name: str) -> TypeDef:
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


def record_resolve(name, field_name, field_typename, field_primitive):
    def resolve(type_reference: TypeReference):
        type_reference.type_def = Record(
            name=name,
            position=0,
            fields=[Record.Field(
                name=field_name,
                position=0,
                type_ref=TypeReference(
                    name=field_typename,
                    position=0,
                    type_def=BaseExternalType(
                        name=field_typename,
                        primitive=field_primitive
                    )
                )
            )],
            constants=[]

        )
    return resolve

def test_parsing_enum(tmp_path: Path):
    parser, _, _ = given(
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
    parser, _, _ = given(
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


def assert_field(field: Record.Field, name: str, typename: str):
    assert field.name == name
    assert field.type_ref.name == typename


def test_parsing_record(tmp_path: Path):
    parser, _, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = record {
            bar: i8;
            baz: i8;
        }
        """
    )

    record = when(parser, Record, "foo")

    fields = record.fields

    # THEN the record should have exactly 2 fields
    assert len(fields) == 2
    assert_field(fields[0], name="bar", typename="i8")
    assert_field(fields[1], name="baz", typename="i8")


def assert_method(method: Interface.Method, name: str, params: list[tuple[str, str]] = None, return_type: str = None,
                  static: bool = False):
    assert method.name == name
    assert method.static == static
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
    parser, _, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +cpp {
                method();
                static static_method();
                method_with_return(): i8;
                method_with_parameter(param: i8);
                method_with_parameters_and_return(param: i8, param2: i8): i8;
            }
            """
    )

    interface = when(parser, Interface, "foo")

    methods = interface.methods

    # THEN the interface should have exactly 5 methods
    assert len(methods) == 5

    # THEN the methods should have the expected names, parameters and attributes
    assert_method(methods[0], "method")
    assert_method(methods[1], "static_method", static=True)
    assert_method(methods[2], "method_with_return", return_type="i8")
    assert_method(methods[3], "method_with_parameter", params=[("param", "i8")])
    params = [("param", "i8"), ("param2", "i8")]
    assert_method(methods[4], "method_with_parameters_and_return", params=params, return_type="i8")
    assert "cpp" in interface.targets
    assert len(interface.targets) == 1


def test_parsing_interface_unknown_target(tmp_path: Path):
    # GIVEN an idl file that references an unknown target language for the defined interface
    parser, _, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +foo {
                method();
            }
            """
    )
    # WHEN parsing the input
    # THEN a IdlParser.UnknownInterfaceTargetException should be raised
    with pytest.raises(IdlParser.UnknownInterfaceTargetException):
        parser.parse()


def test_parsing_interface_no_target(tmp_path: Path):
    # GIVEN an idl file that references no target language for the defined interface
    parser, _, _ = given(
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
    parser, _, _ = given(
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


def test_parsing_invalid_input(tmp_path: Path):
    parser, _, _ = given(
        tmp_path=tmp_path,
        input_idl="****",
    )

    # WHEN parsing the input
    # THEN a IdlParser.ParsingException should be raised
    with pytest.raises(IdlParser.ParsingException):
        parser.parse()


def test_parsing_missing_type(tmp_path):
    # GIVEN an input with an unknown type reference
    parser, resolver_mock, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = record {
            foo: bar;
        }
        """
    )

    def resolve(type_reference: TypeReference):
        raise Resolver.TypeResolvingException(type_reference, 0)

    resolver_mock.resolve.side_effect = resolve

    # WHEN parsing the input
    # THEN a IdlParser.TypeResolvingException should be raised
    with pytest.raises(IdlParser.TypeResolvingException):
        parser.parse()


def test_parsing_duplicate_type(tmp_path: Path):
    # GIVEN an input that redefines an existing type
    parser, resolver_mock, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            i8 = record {
                foo: i8;
            }
            """
    )

    def register(datatype: BaseType):
        raise Resolver.DuplicateTypeException(datatype, 0)

    resolver_mock.register.side_effect = register

    # WHEN parsing the input
    # THEN a IdlParser.DuplicateTypeException should be raised
    with pytest.raises(IdlParser.DuplicateTypeException):
        parser.parse()


def test_parsing_non_existing_file(tmp_path: Path):
    parser, _, _ = given(
        tmp_path=tmp_path,
        input_idl=""
    )
    parser.idl = tmp_path / 'test.djinni'

    # WHEN parsing a file that does not exist
    # THEN a FileNotFoundException should be raised
    with pytest.raises(FileNotFoundException):
        parser.parse()


def test_marshalling_error(tmp_path: Path):
    # GIVEN input that cannot be marshalled by one of the registered Marshals
    parser, _, marshal_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            i8 = record {
                foo: i8;
            }
            """
    )

    def marshal(input_def: BaseType | BaseField):
        raise Marshal.MarshalException(input_def, "")

    marshal_mock.marshal.side_effect = marshal

    # WHEN parsing the input
    # THEN a IdlParser.MarshallingException should be raised
    with pytest.raises(IdlParser.MarshallingException):
        parser.parse()


def test_import(tmp_path: Path):
    # GIVEN an idl file that imports another file
    parser, _, _ = given(
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
    parser, _, _ = given(
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
    parser, resolver_mock, _ = given(
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
    parser, resolver_mock, _ = given(
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
    parser, _, _ = given(
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
    parser, resolver_mock, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
        foo = record {{
            const bar: {typename} = {literal_value};
        }}
        """
    )

    # AND GIVEN a resolver that returns the matching primitive type
    def resolve(type_reference: TypeReference):
        type_reference.type_def = BaseExternalType(
            name=typename,
            primitive=primitive
        )

    resolver_mock.resolve.side_effect = resolve

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
    parser, resolver_mock, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
            foo = record {{
                const bar: {typename} = {literal_value};
            }}
            """
    )

    # AND GIVEN a resolver that returns a primitive type that does not match the provided const value
    def resolve(type_reference: TypeReference):
        type_reference.type_def = BaseExternalType(
            name=typename,
            primitive=primitive
        )

    resolver_mock.resolve.side_effect = resolve

    # WHEN parsing the idl
    # THEN a Parsing exception should be thrown
    with pytest.raises(IdlParser.ParsingException):
        when(parser, Record, "foo")


@pytest.mark.parametrize("literal_value", [
    '5', '5.5', 'false', 'true', '"test"', '{a="foo"}', '{a=5.5}', '{a=true}'
])
def test_record_wrong_const_record_assignment(tmp_path, literal_value):
    # GIVEN an idl file that assigns a primitive value to a const record type
    parser, resolver_mock, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
                bar = record {{
                    const b: foo = {literal_value};
                }}
                """
    )

    resolver_mock.resolve.side_effect = record_resolve("foo", "a", "i8", BaseExternalType.Primitive.int)

    # WHEN parsing the file
    # THEN a InvalidAssignmentException should be raised
    with pytest.raises(IdlParser.InvalidAssignmentException):
        parser.parse()


def test_record_wrong_const_unknown_field_assignment(tmp_path):
    # GIVEN an idl file that assigns an object with an unknown field to a const value
    parser, resolver_mock, _ = given(
        tmp_path=tmp_path,
        input_idl="""
                    bar = record {
                        const b: foo = {b=5};
                    }
                    """
    )

    resolver_mock.resolve.side_effect = record_resolve("foo", "a", "i8", BaseExternalType.Primitive.int)

    # WHEN parsing the file
    # THEN a InvalidAssignmentException should be raised
    with pytest.raises(IdlParser.UnknownFieldException):
        parser.parse()
