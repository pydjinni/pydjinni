from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from jinja2 import Environment, PackageLoader

from pydjinni.config.config_model_factory import ConfigModelFactory
from pydjinni.generator.file_writer import FileWriter
from pydjinni.parser.ast import Flags, Enum, Record, Interface, BaseType
from .marshal import Marshal
from ..parser.type_model_factory import TypeModelFactory


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
            config_factory: ConfigModelFactory,
            external_type_model_factory: TypeModelFactory,
            logger: Logger):
        self._file_writer = file_writer
        self._logger = logger
        module = '.'.join(self.__module__.split('.')[:-1])
        self._jinja_env = Environment(
            loader=PackageLoader(module, "templates")
        )
        self.marshal = self._marshal_type(
            key=self.key,
            config_factory=config_factory,
            external_type_model_factory=external_type_model_factory,
            logger=logger
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
