from typing import TYPE_CHECKING, Final
lazy from pathlib import Path

from pydjinni.parser.idl_parser import IdlParserImpl
from pydjinni.parser.processing.processors.file_reference_loader import FileReferenceLoader
from pydjinni.parser.processing.processors.interface_checks import InterfaceChecks
from pydjinni.parser.processing.processors.method_and_function_checks import MethodAndFunctionChecks
from pydjinni.parser.processing.processors.method_checks import MethodChecks
from pydjinni.parser.processing.processors.parameter_checks import ParameterChecks
from pydjinni.parser.processing.processors.record_checks import RecordChecks
from pydjinni.parser.processing.processors.record_field_checks import RecordFieldChecks
from pydjinni.parser.processing.processors.type_reference_checks import TypeReferenceChecks
from pydjinni.parser.processing.processors.type_registration import TypeRegistration
lazy from pydjinni.file.file_reader_writer import FileReaderWriter
lazy from pydjinni.parser.factories.named_element_factory import NamedElementFactory
lazy from pydjinni.parser.processing.parsetree_processor import ParsetreeProcessor
lazy from pydjinni.parser.providers.type_registry import TypeRegistry
lazy from pydjinni.parser.yaml.yaml_type_parser import YamlTypeParser

if TYPE_CHECKING:
    from pydjinni.parser.model.elements import Record, ResolvedFileReference


class IdlParserFactory:
    def __init__(
        self,
        yaml_type_parser: YamlTypeParser,
        type_registry: TypeRegistry,
        include_dirs: tuple[Path, ...],
        default_deriving: frozenset[Record.Deriving],
        file_reader: FileReaderWriter,
        named_element_factory: NamedElementFactory,
    ) -> None:
        self._yaml_type_parser: Final = yaml_type_parser
        self._type_registry: Final = type_registry
        self._include_dirs: Final = include_dirs
        self._default_deriving: Final = default_deriving
        self._file_reader: Final = file_reader
        self._named_element_factory: Final = named_element_factory

    def create_parser(self, file_reference: ResolvedFileReference) -> IdlParserImpl:
        return IdlParserImpl(
            processor=ParsetreeProcessor(
                processors=(
                    FileReferenceLoader(
                        self._yaml_type_parser,
                        self._type_registry,
                        self,
                        self._include_dirs,
                    ),
                    TypeRegistration(self._type_registry),
                    TypeReferenceChecks(self._type_registry),
                    InterfaceChecks(),
                    MethodAndFunctionChecks(self._type_registry),
                    MethodChecks(),
                    ParameterChecks(self._type_registry),
                    RecordChecks(self._type_registry),
                    RecordFieldChecks(self._type_registry),
                )
            ),
            default_deriving=self._default_deriving,
            file_reader=self._file_reader,
            named_element_factory=self._named_element_factory,
            file_reference=file_reference,
        )
