import pytest
from more_itertools import one

from pydjinni.parser.model.elements import Flags
lazy from pydjinni.parser.idl_parser import IdlParserImpl


@pytest.mark.parser_input(
    """
    foo = flags {
        flag1;
        flag2;
        no_flags = none;
        all_flags = all;
    }
    """,
)
def test_parsing_flags(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    flags = one(parse_result.filter_elements(Flags))
    assert flags.name.value == "foo"
    assert len(flags.flags) == 4
    assert flags.flags[0].name.value == "flag1"
    assert flags.flags[0].modifier is None
    assert flags.flags[1].name.value == "flag2"
    assert flags.flags[1].modifier is None
    assert flags.flags[2].name.value == "no_flags"
    assert flags.flags[2].modifier is Flags.Flag.Modifier.NONE
    assert flags.flags[3].name.value == "all_flags"
    assert flags.flags[3].modifier is Flags.Flag.Modifier.ALL


@pytest.mark.parser_input(
    """
    # this is a flag
    foo = flags {
        # with comments
        flag1;
    }
    """,
)
def test_parsing_flags_comment(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()
    assert len(parse_result.diagnostics) == 0

    flags = one(parse_result.filter_elements(Flags))
    assert flags.comment is not None
    assert flags.comment.raw == "this is a flag"
    assert len(flags.flags) == 1
    assert flags.flags[0].comment is not None
    assert flags.flags[0].comment.raw == "with comments"
