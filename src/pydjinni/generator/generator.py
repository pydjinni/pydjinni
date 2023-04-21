from abc import ABC, abstractmethod
from pathlib import Path

from jinja2 import Environment, PackageLoader

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import ConfigurationException
from pydjinni.generator.file_writer import FileWriter
from pydjinni.parser.ast import Flags, Enum, Record, Interface, BaseType
from pydjinni.parser.type_model_builder import TypeModelBuilder
from .marshal import Marshal


class Generator(ABC):
    """
    Abstract class for defining generators. Each generator can utilize one or more Marshal classes, specified as
    generic arguments.
    """

    def __init_subclass__(cls, key: str, marshal: type[Marshal]) -> None:
        cls._marshal_type = marshal
        cls.key = key

    def __init__(
            self,
            file_writer: FileWriter,
            config_model_builder: ConfigModelBuilder,
            external_type_model_builder: TypeModelBuilder):
        self._file_writer = file_writer
        module = '.'.join(self.__module__.split('.')[:-1])
        self._jinja_env = Environment(
            loader=PackageLoader(module, "templates")
        )
        self.marshal = self._marshal_type(
            key=self.key,
            config_model_builder=config_model_builder,
            external_type_model_builder=external_type_model_builder
        )

    def write(self, file: Path, template: str, type_def: BaseType):
        self._file_writer.write(
            filename=file,
            content=self._jinja_env.get_template(template).render(type_def=type_def, config=self.marshal.config)
        )

    @abstractmethod
    def generate_enum(self, type_def: Enum):
        raise NotImplementedError

    @abstractmethod
    def generate_flags(self, type_def: Flags):
        raise NotImplementedError

    @abstractmethod
    def generate_record(self, type_def: Record):
        raise NotImplementedError

    @abstractmethod
    def generate_interface(self, type_def: Interface):
        raise NotImplementedError

    def generate(self, type_def: BaseType):
        if self.marshal.config:
            match type_def:
                case Enum():
                    self.generate_enum(type_def)
                case Flags():
                    self.generate_flags(type_def)
                case Record():
                    self.generate_record(type_def)
                case Interface():
                    self.generate_interface(type_def)
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")
