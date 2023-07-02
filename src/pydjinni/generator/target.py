from abc import ABC
from pathlib import Path

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFilesModelBuilder
from pydjinni.parser.base_models import BaseType
from pydjinni.parser.type_model_builder import TypeModelBuilder
from .generator import Generator
from .marshal import Marshal
from pydjinni.parser.ast import Record


class Target(ABC):
    """
    Abstract class for defining generation targets. A target combines multiple generators to one entity.
    E.g. to allow Java interop, both a Java and JNI generator are required.
    """

    def __init_subclass__(cls, key: str, generators: list[type[Generator]], supported_deriving: set[Record.Deriving]) -> None:
        """
        Args:
            key: The key that is used by the API/CLI to select the generator.
            generators: The list of generators that is related to this target.
            supported_deriving: A set of supported record deriving. For documentation purposes only.
        """
        cls._generator_types = generators
        cls.supported_deriving = supported_deriving
        cls.key = key

    def __init__(
            self,
            file_reader_writer: FileReaderWriter,
            config_model_builder: ConfigModelBuilder,
            external_type_model_builder: TypeModelBuilder,
            processed_files_model_builder: ProcessedFilesModelBuilder):
        self.generator_instances = [generator(
            file_writer=file_reader_writer,
            config_model_builder=config_model_builder,
            external_type_model_builder=external_type_model_builder,
            processed_files_model_builder=processed_files_model_builder
        ) for generator in self._generator_types]

    def input_file(self, path: Path):
        for generator_instance in self.generator_instances:
            generator_instance.input_file(path)

    def generate(self, ast: list[BaseType], clean: bool = False, copy_support_lib_sources: bool = True):
        for generator_instance in self.generator_instances:
            if clean:
                generator_instance.clean()
            generator_instance.generate(ast, copy_support_lib_sources)

    @property
    def marshals(self) -> list[Marshal]:
        marshals: list[Marshal] = []
        for generator in self.generator_instances:
            marshals.append(generator.marshal)
        return marshals
