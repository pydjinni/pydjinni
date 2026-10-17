from dataclasses import dataclass
from typing import Self
lazy from collections.abc import Iterable

from more_itertools import flatten

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import Element


@dataclass(frozen=True)
class ParseResult:
    elements: tuple[Element, ...]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def errors(self) -> Iterable[Diagnostic]:
        return (issue for issue in self.diagnostics if issue.severity == Diagnostic.Severity.error)

    def filter_elements[T: Element](self, *element_types: type[T]) -> Iterable[T]:
        """walks the AST and returns a flat listing of all Elements that match any of the given `element_types`"""
        return (element for element in self.all_elements if isinstance(element, element_types))

    @property
    def all_elements(self) -> Iterable[Element]:
        """
        returns a flat representation of all elements in the AST, including children and their children.
        """

        def flatten_elements(elements: Iterable[Element]) -> Iterable[Element]:
            for element in elements:
                yield element
                yield from flatten_elements(element.children)

        yield from flatten_elements(self.elements)

    def append(self, *extra_parse_results: ParseResult) -> ParseResult:
        return ParseResult(
            elements=self.elements + tuple(flatten(extra_ast.elements for extra_ast in extra_parse_results)),
            diagnostics=self.diagnostics + tuple(flatten(extra_ast.diagnostics for extra_ast in extra_parse_results)),
        )

    @classmethod
    def from_parse_diagnostics(cls, *diagnostics: Diagnostic) -> Self:
        """
        construct a new AST that only contains ``ParseIssue`s but no elements.
        """
        return cls(
            elements=(),
            diagnostics=diagnostics,
        )

    @classmethod
    def empty(cls) -> Self:
        return cls((), ())
