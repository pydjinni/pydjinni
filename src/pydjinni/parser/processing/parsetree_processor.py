from abc import ABC, abstractmethod
from functools import cached_property
from itertools import product
from typing import Any, Final, cast, final, get_type_hints

from pydjinni.parser.model.elements import Element
lazy from pydjinni.parser.model.parse_result import ParseResult


class Processor[T: Element](ABC):
    @cached_property
    def _element_type(self) -> type[T]:
        annotation = get_type_hints(self.process)["element"]
        return cast("type[T]", annotation)

    @final
    def accepts(self, element: Element) -> bool:
        return isinstance(element, self._element_type)

    @abstractmethod
    def process(self, element: T) -> ParseResult: ...


class ParsetreeProcessor:
    def __init__(self, processors: tuple[Processor[Any], ...]) -> None:
        self._processors: Final = processors

    def process(self, parse_result: ParseResult) -> ParseResult:
        """
        applies all known processors against the current ParseResult.

        Returns:
            ParseResult: a new ParseResult that has been extended with the new elements & issues results.
        """
        return parse_result.append(
            *(
                processor.process(element)
                for processor, element in product(self._processors, parse_result.all_elements)
                if processor.accepts(element)
            ),
        )
