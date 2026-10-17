from typing import Final, override
lazy from collections.abc import Iterable

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import ErrorDomain, Parameter
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
lazy from pydjinni.parser.providers.type_registry import TypeRegistry


class ParameterChecks(Processor[Parameter]):
    def __init__(self, registry: TypeRegistry) -> None:
        self._registry: Final = registry

    @override
    def process(self, element: Parameter) -> ParseResult:
        return ParseResult.from_parse_diagnostics(
            *self._check_parameter_type(element),
        )

    def _check_parameter_type(self, parameter: Parameter) -> Iterable[Diagnostic]:
        definition = self._registry.resolve(parameter.reference)
        if isinstance(definition, ErrorDomain):
            yield Diagnostic(
                position=parameter.reference.position,
                description="Cannot pass an error type as a parameter",
                severity=Diagnostic.Severity.error,
            )
