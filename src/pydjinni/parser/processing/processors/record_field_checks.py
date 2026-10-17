from typing import Final, override
lazy from collections.abc import Iterable

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import ErrorDomain, Function, Interface, Record, Type, TypeReference
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
lazy from pydjinni.parser.providers.type_registry import TypeRegistry


class RecordFieldChecks(Processor[Record.Field]):
    def __init__(self, registry: TypeRegistry) -> None:
        self._registry: Final = registry

    @override
    def process(self, element: Record.Field) -> ParseResult:
        definition = self._registry.resolve(element.reference)
        return ParseResult.from_parse_diagnostics(
            *self._check_field_type(element.reference, definition),
        )

    def _check_field_type(self, reference: TypeReference, definition: Type | None) -> Iterable[Diagnostic]:
        if isinstance(definition, ErrorDomain):
            yield Diagnostic(
                position=reference.position,
                description="Cannot assign an error as record field type",
                severity=Diagnostic.Severity.error,
            )
        elif isinstance(definition, Interface):
            yield Diagnostic(
                position=reference.position,
                description="Cannot assign an interface as record field type",
                severity=Diagnostic.Severity.error,
            )
        elif isinstance(definition, Function):
            yield Diagnostic(
                position=reference.position,
                description="Cannot assign a function as record field type",
                severity=Diagnostic.Severity.error,
            )
