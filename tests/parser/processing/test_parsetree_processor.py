from typing import override
from unittest.mock import Mock

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import Interface, Record, TypeReference
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import ParsetreeProcessor, Processor


def test_parsetree_validator():
    diagnostic = Mock(Diagnostic)

    # GIVEN two Processor implementations
    class FirstProcessor(Processor):
        @override
        def process(self, element: Record) -> ParseResult:
            return ParseResult((), ())

    class SecondProcessor(Processor):
        @override
        def process(self, element: Interface) -> ParseResult:
            return ParseResult((), (diagnostic,))

    # AND GIVEN a ParsetreeProcessor instance with these processors
    parsetree_processor = ParsetreeProcessor(
        processors=(
            FirstProcessor(),
            SecondProcessor(),
        )
    )

    # AND GIVEN a ParseResult
    parse_result = ParseResult(
        (
            Record(
                name=Identifier("foo"),
                fields=(
                    Record.Field(
                        name=Identifier("bar"),
                        reference=TypeReference(
                            name=Identifier("baz"),
                            parameters=(),
                        ),
                    ),
                ),
            ),
            Interface(
                name=Identifier("bar"),
            ),
        ),
        (),
    )

    # WHEN processing the current ParseResult
    new_parse_result = parsetree_processor.process(parse_result)

    # THEN the Elements from the SecondProcessor should be returned
    assert new_parse_result.elements == parse_result.elements

    # THEN the Diagnostic from the second Processor should be returned
    assert new_parse_result.diagnostics == (diagnostic,)
