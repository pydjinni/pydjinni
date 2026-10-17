from typing import Final, override
lazy from collections.abc import Iterable

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import CollectionType, Record
from pydjinni.parser.model.parse_result import ParseResult
from pydjinni.parser.processing.parsetree_processor import Processor
lazy from pydjinni.parser.providers.type_registry import TypeRegistry


class RecordChecks(Processor[Record]):
    def __init__(self, registry: TypeRegistry) -> None:
        self._registry: Final = registry

    @override
    def process(self, element: Record) -> ParseResult:
        return ParseResult.from_parse_diagnostics(
            *self._check_deriving_collection_fields(element),
        )

    def _check_deriving_collection_fields(self, record: Record) -> Iterable[Diagnostic]:
        if Record.Deriving.ord in record.deriving:
            for field in record.fields:
                definition = self._registry.resolve(field.reference)
                if isinstance(definition, CollectionType):
                    yield Diagnostic(
                        position=field.position,
                        description=f"Cannot compare collections in '{Record.Deriving.ord}' deriving",
                        severity=Diagnostic.Severity.error,
                    )
