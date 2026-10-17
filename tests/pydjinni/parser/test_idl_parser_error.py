import pytest
from more_itertools import one

from pydjinni.parser.model.elements import ErrorDomain
lazy from pydjinni.parser.idl_parser import IdlParserImpl


@pytest.mark.parser_input(
    """
	foo = error {
		bar;
		baz(param: i8);
	}
	""",
)
def test_parsing_error(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    error_domain = one(parse_result.filter_elements(ErrorDomain))
    assert error_domain.name.value == "foo"
    assert len(error_domain.error_codes) == 2

    bar, baz = error_domain.error_codes
    assert bar.name.value == "bar"
    assert len(bar.parameters) == 0
    assert baz.name.value == "baz"
    assert len(baz.parameters) == 1
    assert baz.parameters[0].name.value == "param"
    assert baz.parameters[0].reference.name.value == "i8"


@pytest.mark.parser_input(
    """
	# This is an error domain with a comment
	foo = error {
		# This is an error code
		baz;
	}
	""",
)
def test_parsing_error_comment(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    error_domain = one(parse_result.filter_elements(ErrorDomain))
    assert error_domain.comment is not None
    assert error_domain.comment.raw == "This is an error domain with a comment"
    assert len(error_domain.error_codes) == 1
    error_code = error_domain.error_codes[0]
    assert error_code.comment is not None
    assert error_code.comment.raw == "This is an error code"


@pytest.mark.parser_input(
    """
	foo = error {}
	""",
)
def test_parsing_error_no_codes(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    error_domain = one(parse_result.filter_elements(ErrorDomain))
    assert error_domain.name.value == "foo"
    assert len(error_domain.error_codes) == 0
