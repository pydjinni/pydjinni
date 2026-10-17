from typing import override
lazy from collections.abc import Iterable

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
lazy from pydjinni.parser.model.elements import Interface


class MethodChecks(Processor[Interface.Method]):
    @override
    def process(self, element: Interface.Method) -> ParseResult:
        return ParseResult.from_parse_diagnostics(*self._check_method_static_const(element))

    def _check_method_static_const(self, method: Interface.Method) -> Iterable[Diagnostic]:
        if method.static and method.const:
            yield Diagnostic(
                position=method.position,
                description="method cannot be both static and const",
                severity=Diagnostic.Severity.error,
            )
