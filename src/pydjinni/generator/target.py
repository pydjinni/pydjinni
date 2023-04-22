from abc import ABC
from pathlib import Path

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.generator.file_writer import FileWriter
from pydjinni.parser.base_models import BaseType
from pydjinni.parser.type_model_builder import TypeModelBuilder
from .generator import Generator
from .marshal import Marshal


class Target(ABC):
    """
    Abstract class for defining generation targets. A target combines multiple generators to one entity.
    E.g. to allow Java interop, both a Java and JNI generator are required.
    """

    def __init_subclass__(cls, key: str, generators: list[type[Generator]]) -> None:
        cls._generator_types = generators
        cls.key = key

    def __init__(
            self,
            file_writer: FileWriter,
            config_model_builder: ConfigModelBuilder,
            external_type_model_builder: TypeModelBuilder):
        self.generator_instances = [generator(
            file_writer=file_writer,
            config_model_builder=config_model_builder,
            external_type_model_builder=external_type_model_builder
        ) for generator in self._generator_types]

    def input_file(self, path: Path):
        for generator_instance in self.generator_instances:
            generator_instance.input_file(path)

    def generate(self, ast: list[BaseType]):
        for generator_instance in self.generator_instances:
            generator_instance.generate(ast)

    @property
    def marshals(self) -> list[Marshal]:
        marshals: list[Marshal] = []
        for generator in self.generator_instances:
            marshals.append(generator.marshal)
        return marshals
