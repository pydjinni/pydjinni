import pytest
from more_itertools import one

from pydjinni.parser.model.elements import Interface
lazy from pydjinni.parser.idl_parser import IdlParserImpl


@pytest.mark.parser_input(
    """
    foo = interface {
        method();
        static static_method();
        const const_method();
        async async_method();
        static async static_async_method();
        method_with_return() -> i8;
        method_with_parameter(param: i8);
        method_with_parameters_and_return(param: i8, param2: i8) -> i8;
        method_throwing() throws;
        method_throwing_and_return() throws -> i8;
        method_throwing_specific_error() throws application_error;
        method_throwing_specific_error_and_return() throws application_error -> i8;
        a: i8;
        readonly b: i8;
    }
    """,
)
def test_parsing_interface(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    interface = one(parse_result.filter_elements(Interface))
    assert interface.name.value == "foo"
    assert interface.host
    assert interface.native

    methods = interface.methods
    assert len(methods) == 12
    assert methods[0].name.value == "method"
    assert not methods[0].static
    assert not methods[0].const
    assert not methods[0].asynchronous
    assert methods[1].name.value == "static_method"
    assert methods[1].static
    assert methods[2].name.value == "const_method"
    assert methods[2].const
    assert methods[3].name.value == "async_method"
    assert methods[3].asynchronous
    assert methods[4].static and methods[4].asynchronous
    assert methods[5].return_reference is not None
    assert methods[5].return_reference.name.value == "i8"
    assert methods[6].parameters[0].name.value == "param"
    assert methods[6].parameters[0].reference.name.value == "i8"
    assert [parameter.name.value for parameter in methods[7].parameters] == ["param", "param2"]
    assert methods[7].return_reference is not None
    assert methods[7].return_reference.name.value == "i8"
    assert methods[8].throwing == ()
    assert methods[9].throwing == ()
    assert methods[9].return_reference is not None
    assert methods[10].throwing[0].name.value == "application_error"
    assert methods[11].throwing[0].name.value == "application_error"
    assert methods[11].return_reference is not None

    assert len(interface.properties) == 2
    assert interface.properties[0].name.value == "a"
    assert interface.properties[0].reference.name.value == "i8"
    assert not interface.properties[0].readonly
    assert interface.properties[1].name.value == "b"
    assert interface.properties[1].reference.name.value == "i8"
    assert interface.properties[1].readonly


@pytest.mark.parametrize(
    ("expected_host", "expected_native"),
    [
        pytest.param(
            True,
            False,
            id="host",
            marks=pytest.mark.parser_input(
                "foo = host interface {}",
            ),
        ),
        pytest.param(
            False,
            True,
            id="native",
            marks=pytest.mark.parser_input(
                "foo = native interface {}",
            ),
        ),
        pytest.param(
            True,
            True,
            id="shared",
            marks=pytest.mark.parser_input(
                "foo = shared interface {}",
            ),
        ),
    ],
)
def test_parsing_interface_targets(idl_parser: IdlParserImpl, expected_host: bool, expected_native: bool):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    interface = one(parse_result.filter_elements(Interface))
    assert interface.host == expected_host
    assert interface.native == expected_native


@pytest.mark.parser_input(
    """
    # this interface is awesome
    # it supports multiline comments
    foo = interface {
        # this is the static initializer
        static init_foo() -> foo;

        # this is a property
        foo: i8;
    }
    """,
)
def test_parsing_interface_comment(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    interface = one(parse_result.filter_elements(Interface))
    assert interface.comment is not None
    assert interface.comment.raw == "this interface is awesome\nit supports multiline comments"
    assert interface.methods[0].comment is not None
    assert interface.methods[0].comment.raw == "this is the static initializer"
    assert interface.properties[0].comment is not None
    assert interface.properties[0].comment.raw == "this is a property"


@pytest.mark.parser_input(
    """
    # @deprecated but it should not be used
    foo = interface {
        # @param bar is a bar
        # @returns a foo instance
        # @deprecated
        init_foo(bar: i8) -> foo;
    }
    """,
)
def test_parsing_comment_commands(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    interface = one(parse_result.filter_elements(Interface))
    method = interface.methods[0]
    assert interface.comment is not None
    assert interface.comment.deprecated is not False
    assert method.comment is not None
    assert method.comment.deprecated is True
    assert "bar" in method.comment.parameters
