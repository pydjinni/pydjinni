import pytest
from more_itertools import one

from pydjinni.parser.model.elements import Record
lazy from pydjinni.parser.idl_parser import IdlParserImpl


@pytest.mark.parser_input(
    """
	foo = record {
		bar: i8;
		baz: i8?;
	}
	""",
)
def test_parsing_record(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    record = one(parse_result.filter_elements(Record))
    assert record.name.value == "foo"
    assert len(record.fields) == 2
    assert record.fields[0].name.value == "bar"
    assert record.fields[0].reference.name.value == "i8"
    assert not record.fields[0].reference.optional
    assert record.fields[1].name.value == "baz"
    assert record.fields[1].reference.name.value == "i8"
    assert record.fields[1].reference.optional


@pytest.mark.parser_input(
    """
	foo = record {} deriving (ord, eq)
	""",
)
def test_parsing_record_deriving(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    record = one(parse_result.filter_elements(Record))
    assert record.deriving == frozenset({Record.Deriving.ord, Record.Deriving.eq})


# TODO test default deriving


@pytest.mark.parser_input(
    """
	# This is a record
	# with a comment
	foo = record {
		# This is a record field
		baz: i8;
	}
	""",
)
def test_parsing_record_comment(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    record = one(parse_result.filter_elements(Record))
    assert record.comment is not None
    assert record.comment.raw == "This is a record\nwith a comment"
    assert record.fields[0].comment is not None
    assert record.fields[0].comment.raw == "This is a record field"


# TODO test records with targets (+cpp, ...)
