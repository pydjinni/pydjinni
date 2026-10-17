import pytest
from more_itertools import one

from pydjinni.parser.model.elements import Function, Interface
lazy from pydjinni.parser.idl_parser import IdlParserImpl


@pytest.mark.parser_input(
    """
	foo = function (param: i8) -> bool;
	""",
)
def test_parsing_function(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    function = one(parse_result.filter_elements(Function))
    assert function.name.value == "foo"
    assert not function.anonymous
    assert len(function.parameters) == 1
    assert function.parameters[0].name.value == "param"
    assert function.parameters[0].reference.name.value == "i8"
    assert function.return_reference is not None
    assert function.return_reference.name.value == "bool"
    assert function.throwing == ()
    assert function.native
    assert function.host


@pytest.mark.parametrize(
    ("expected_native", "expected_host"),
    [
        pytest.param(
            True,
            True,
            id="default",
            marks=pytest.mark.parser_input(
                "foo = function (param: i8) -> bool;",
            ),
        ),
        pytest.param(
            True,
            True,
            id="brief",
            marks=pytest.mark.parser_input(
                "foo = (param: i8) -> bool;",
            ),
        ),
        pytest.param(
            False,
            True,
            id="host",
            marks=pytest.mark.parser_input(
                "foo = host function (param: i8) -> bool;",
            ),
        ),
        pytest.param(
            True,
            True,
            id="shared",
            marks=pytest.mark.parser_input(
                "foo = shared function (param: i8) -> bool;",
            ),
        ),
        pytest.param(
            True,
            False,
            id="native",
            marks=pytest.mark.parser_input(
                "foo = native function (param: i8) -> bool;",
            ),
        ),
    ],
)
def test_parsing_function_targets(idl_parser: IdlParserImpl, expected_native: bool, expected_host: bool):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    function = one(parse_result.filter_elements(Function))
    assert function.name.value == "foo"
    assert function.native == expected_native
    assert function.host == expected_host


@pytest.mark.parametrize(
    ("expected_name", "expected_host", "expected_native"),
    [
        pytest.param(
            "function_shared_i8_void",
            True,
            True,
            id="default",
            marks=pytest.mark.parser_input(
                """
                foo = interface {
                    method0(callback: (var: i8));
                }
                """,
            ),
        ),
        pytest.param(
            "function_shared_i8_void",
            True,
            True,
            id="default",
            marks=pytest.mark.parser_input(
                """
                foo = interface {
                    method0(callback: function (var: i8));
                }
                """,
            ),
        ),
        pytest.param(
            "function_host_i8_void",
            True,
            False,
            id="host",
            marks=pytest.mark.parser_input(
                """
                foo = interface {
                    method0(callback: host function (var: i8));
                }
                """,
            ),
        ),
        pytest.param(
            "function_native_i8_void",
            False,
            True,
            id="native",
            marks=pytest.mark.parser_input(
                """
                foo = interface {
                    method0(callback: native function (var: i8));
                }
                """,
            ),
        ),
    ],
)
def test_parsing_anonymous_inline_function(
    idl_parser: IdlParserImpl, expected_name: str, expected_host: bool, expected_native: bool
):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    function = one(parse_result.filter_elements(Function))
    assert function.name.value == expected_name
    assert function.anonymous
    assert len(function.parameters) == 1
    assert function.parameters[0].name.value == "var"
    assert function.parameters[0].reference.name.value == "i8"
    assert function.return_reference is None
    assert function.host == expected_host
    assert function.native == expected_native
    assert one(parse_result.filter_elements(Interface)).methods[0].parameters[0].reference.inline_function is function


@pytest.mark.parser_input(
    """
	foo = function () throws;
	""",
)
def test_parsing_function_throwing(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    function = one(parse_result.filter_elements(Function))
    assert function.throwing == ()


@pytest.mark.parser_input(
    """
	foo = function () throws bar;
	""",
)
def test_parsing_function_throwing_specific_error(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    function = one(parse_result.filter_elements(Function))
    assert len(function.throwing) == 1
    assert function.throwing[0].name.value == "bar"


@pytest.mark.parser_input(
    """
	# this function does nothing
	foo = function ();
	""",
)
def test_parsing_function_comment(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    function = one(parse_result.filter_elements(Function))
    assert function.comment is not None
    assert function.comment.raw == "this function does nothing"
