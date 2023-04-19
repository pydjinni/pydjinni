from abc import ABC
from logging import Logger

from pydjinni.config.config_model_factory import ConfigModelFactory
from pydjinni.generator.file_writer import FileWriter
from .generator import Generator
from .marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.type_model_factory import TypeModelFactory
from ..parser.base_models import BaseType


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
            config_factory: ConfigModelFactory,
            external_type_model_factory: TypeModelFactory,
            logger: Logger):
        self.generator_instances = [generator(
            file_writer=file_writer,
            config_factory=config_factory,
            external_type_model_factory=external_type_model_factory,
            logger=logger
        ) for generator in self._generator_types]

    def generate_enum(self, type_def: Enum):
        for generator_instance in self.generator_instances:
            generator_instance.generate_enum(type_def)

    def generate_flags(self, type_def: Flags):
        for generator_instance in self.generator_instances:
            generator_instance.generate_flags(type_def)

    def generate_record(self, type_def: Record):
        for generator_instance in self.generator_instances:
            generator_instance.generate_record(type_def)

    def generate_interface(self, type_def: Interface):
        for generator_instance in self.generator_instances:
            generator_instance.generate_interface(type_def)

    @property
    def marshals(self) -> list[Marshal]:
        marshals: list[Marshal] = []
        for generator in self.generator_instances:
            marshals.append(generator.marshal)
        return marshals

    def generate(self, type_def: BaseType):
        match type_def:
            case Enum():
                self.generate_enum(type_def)
            case Flags():
                self.generate_flags(type_def)
            case Record():
                self.generate_record(type_def)
            case Interface():
                self.generate_interface(type_def)
