from typing import TYPE_CHECKING, Final

from pydjinni.parser.idl_parser import IdlParserImpl
lazy from pydjinni.file.file_reader_writer import FileReaderWriter
lazy from pydjinni.parser.factories.named_element_factory import NamedElementFactory
lazy from pydjinni.parser.processing.parsetree_processor import ParsetreeProcessor

if TYPE_CHECKING:
    from pydjinni.parser.model.elements import Record, ResolvedFileReference


class ParserFactory:
    def __init__(
        self,
        processor: ParsetreeProcessor,
        default_deriving: frozenset[Record.Deriving],
        file_reader: FileReaderWriter,
        named_element_factory: NamedElementFactory,
    ) -> None:
        self._processor: Final = processor
        self._default_deriving: Final = default_deriving
        self._file_reader: Final = file_reader
        self._named_element_factory: Final = named_element_factory

    def create_parser(self, file_reference: ResolvedFileReference) -> IdlParserImpl:
        return IdlParserImpl(
            processor=self._processor,
            default_deriving=self._default_deriving,
            file_reader=self._file_reader,
            named_element_factory=self._named_element_factory,
            file_reference=file_reference,
        )
