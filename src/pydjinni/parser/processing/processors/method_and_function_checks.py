from typing import Final, override
lazy from collections.abc import Iterable

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import ErrorDomain, Function, Interface
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
lazy from pydjinni.parser.providers.type_registry import TypeRegistry


class MethodAndFunctionChecks(Processor[Interface.Method | Function]):
    def __init__(self, registry: TypeRegistry) -> None:
        self._registry: Final = registry

    @override
    def process(self, element: Interface.Method | Function) -> ParseResult:
        return ParseResult.from_parse_diagnostics(
            *self._check_return_type(element),
            *self._check_throw_types(element),
        )

    def _check_return_type(self, element: Interface.Method | Function) -> Iterable[Diagnostic]:
        if element.return_reference:
            definition = self._registry.resolve(element.return_reference)
            if isinstance(definition, ErrorDomain):
                yield Diagnostic(
                    position=element.return_reference.position,
                    description="Cannot return an error type",
                    severity=Diagnostic.Severity.error,
                )

    def _check_throw_types(self, element: Interface.Method | Function) -> Iterable[Diagnostic]:
        for reference in element.throwing:
            definition = self._registry.resolve(reference)
            if definition and not isinstance(definition, ErrorDomain):
                yield Diagnostic(
                    position=reference.position,
                    description="Only errors can be thrown",
                    severity=Diagnostic.Severity.error,
                )
