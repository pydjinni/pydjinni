from pathlib import Path

import pytest
from dirty_equals import HasAttributes, IsInstance, IsTuple
from more_itertools import one

from pydjinni.parser.model.elements import Enum, ExternTypeReference, ImportReference, Namespace
lazy from pydjinni.parser.idl_parser import IdlParserImpl


@pytest.mark.parser_input("****")
def test_parsing_invalid_input(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()

    assert len(parse_result.diagnostics) == 4
    assert all(issue.severity is issue.Severity.error for issue in parse_result.diagnostics)


@pytest.mark.parser_input('@import "foo.pydjinni"')
def test_import(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()

    assert len(parse_result.diagnostics) == 0
    import_reference = one(parse_result.filter_elements(ImportReference))
    assert import_reference.file_reference.path == Path("foo.pydjinni")


@pytest.mark.parser_input('@extern "extern.yaml"')
def test_extern(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()

    assert len(parse_result.diagnostics) == 0
    extern_reference = one(parse_result.filter_elements(ExternTypeReference))
    assert extern_reference.file_reference.path == Path("extern.yaml")


@pytest.mark.parser_input(
    """
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
def test_namespace(idl_parser: IdlParserImpl):
    parse_result = idl_parser.parse()

    assert len(parse_result.diagnostics) == 0

    assert parse_result.elements == IsTuple(
        IsInstance(Namespace)
        & HasAttributes(
            name=HasAttributes(value="bar"),
            namespace=HasAttributes(values=IsTuple(HasAttributes(value="foo"))),
            types=IsTuple(
                IsInstance(Enum)
                & HasAttributes(
                    name=HasAttributes(value="foo"),
                    namespace=HasAttributes(
                        values=IsTuple(HasAttributes(value="foo"), HasAttributes(value="bar")),
                    ),
                )
            ),
            namespaces=IsTuple(
                HasAttributes(
                    name=HasAttributes(value="baz"),
                    namespace=HasAttributes(
                        values=IsTuple(HasAttributes(value="foo"), HasAttributes(value="bar")),
                    ),
                    types=IsTuple(
                        IsInstance(Enum)
                        & HasAttributes(
                            name=HasAttributes(value="bar"),
                            namespace=HasAttributes(
                                values=IsTuple(
                                    HasAttributes(value="foo"),
                                    HasAttributes(value="bar"),
                                    HasAttributes(value="baz"),
                                ),
                            ),
                        )
                    ),
                )
            ),
        )
    )
