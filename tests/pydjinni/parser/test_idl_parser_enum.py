import pytest
from more_itertools import one

from pydjinni.parser.model.elements import Enum
lazy from pydjinni.parser.idl_parser import IdlParserImpl


@pytest.mark.parser_input(
    """
	foo = enum {
		first_item;
		second_item;
	}
	""",
)
def test_parsing_enum(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    enum = one(parse_result.filter_elements(Enum))
    assert enum.name.value == "foo"
    assert len(enum.items) == 2
    assert enum.items[0].name.value == "first_item"
    assert enum.items[1].name.value == "second_item"


@pytest.mark.parser_input(
    """
	# this is an enum
	foo = enum {
		# with comments
		first_item;
	}
	""",
)
def test_parsing_enum_comment(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    enum = one(parse_result.filter_elements(Enum))
    assert enum.comment is not None
    assert enum.comment.raw == "this is an enum"
    assert len(enum.items) == 1
    assert enum.items[0].comment is not None
    assert enum.items[0].comment.raw == "with comments"
