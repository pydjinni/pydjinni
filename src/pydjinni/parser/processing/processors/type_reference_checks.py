from typing import Final, override
lazy from collections.abc import Iterable

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import GenericType, Type, TypeReference
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
from pydjinni.parser.providers.type_registry import TypeRegistry


class TypeReferenceChecks(Processor[TypeReference]):
    def __init__(self, registry: TypeRegistry) -> None:
        self._registry: Final = registry

    @override
    def process(self, element: TypeReference) -> ParseResult:
        try:
            definition = self._registry.resolve(element)
            return ParseResult.from_parse_diagnostics(
                *self._check_type_parameters(element, definition),
            )
        except TypeRegistry.TypeResolvingException as e:
            if e.reference.required_resolution:
                severity = Diagnostic.Severity.error
            else:
                severity = Diagnostic.Severity.warning
            return ParseResult.from_parse_diagnostics(
                Diagnostic(
                    position=e.reference.position,
                    description=f"Unknown type '{e.reference.name.value}'",
                    severity=severity,
                )
            )

    def _check_type_parameters(self, reference: TypeReference, definition: Type) -> Iterable[Diagnostic]:
        if isinstance(definition, GenericType) and definition.params:
            if not reference.parameters:
                yield Diagnostic(
                    position=reference.position,
                    description=f"Missing generic parameters for '{definition.name.value}<{', '.join(definition.params)}>'.",
                    severity=Diagnostic.Severity.error,
                )
            elif len(reference.parameters) != len(definition.params):
                yield Diagnostic(
                    position=reference.position,
                    description=f"Invalid number of generic parameters given to '{definition.name.value}<{', '.join(definition.params)}>'. "
                    f"Expects {len(definition.params)}, but {len(reference.parameters)} were given.",
                    severity=Diagnostic.Severity.error,
                )

        elif reference.parameters:
            yield Diagnostic(
                position=reference.position,
                description=f"Type '{reference.name.value}' does not accept generic parameters",
                severity=Diagnostic.Severity.error,
            )
