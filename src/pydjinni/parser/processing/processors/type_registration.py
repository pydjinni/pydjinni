from typing import Final, override

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
from pydjinni.parser.providers.type_registry import TypeRegistry
lazy from pydjinni.parser.model.elements import Type


class TypeRegistration(Processor["Type"]):
    def __init__(self, type_registry: TypeRegistry) -> None:
        self._type_registry: Final = type_registry

    @override
    def process(self, element: Type) -> ParseResult:
        try:
            self._type_registry.register(element)
            return ParseResult.empty()
        except TypeRegistry.DuplicateTypeException as e:
            return ParseResult.from_parse_diagnostics(
                Diagnostic(
                    position=e.new_type.position,
                    description="Duplicate type detected",
                    severity=Diagnostic.Severity.error,
                    related_information=(
                        Diagnostic.RelatedInformation(
                            position=e.existing_type.position,
                            description="Previous type definition is here.",
                        ),
                    ),
                )
            )
