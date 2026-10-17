from typing import override
lazy from collections.abc import Iterable

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
lazy from pydjinni.parser.model.elements import Interface


class InterfaceChecks(Processor[Interface]):
    @override
    def process(self, element: Interface) -> ParseResult:
        return ParseResult.from_parse_diagnostics(
            *self._check_static_method_target(element),
        )

    def _check_static_method_target(self, interface: Interface) -> Iterable[Diagnostic]:
        for method in interface.methods:
            if method.static and interface.host:
                yield Diagnostic(
                    position=method.position,
                    description="static methods are only allowed on native or main interfaces",
                    severity=Diagnostic.Severity.error,
                )
