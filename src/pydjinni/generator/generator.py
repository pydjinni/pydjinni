import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import NoReturn

from jinja2 import Environment, PackageLoader, FileSystemLoader

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
        self._input_file = None
        self._generator_directory = Path(inspect.getfile(self.__class__)).parent
        self._jinja_env = Environment(
            loader=FileSystemLoader(self._generator_directory / "templates")
        )
        self.marshal = self._marshal_type(
            key=self.key,
            config_model_builder=config_model_builder,
            external_type_model_builder=external_type_model_builder
        )

    def input_file(self, path: Path):
        """Sets the input file that is currently being processed."""
        self._input_file = path

    def write(self, file: Path, template: str, **kwargs):
        """
        Renders a Jinja2 template with the provided arguments.

        Args:
            file: the filename of the file that should be rendered
            template: the template file to be used for rendering
            **kwargs: any other args are directly passed to the jinja template
        """
        self._file_writer.write(
            filename=file,
            content=self._jinja_env.get_template(template).render(
                config=self.marshal.config,
                input_file=self._input_file,
                **kwargs
            )
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

    def generate_support_lib(self):
        """
        Copies support lib files if they exist. Fails silently if no files can be found in the expected directories.
        """
        self._file_writer.copy_directory(
            source_dir=self._generator_directory / "support_lib" / "include",
            target_dir=self.marshal.source_path()
        )
        self._file_writer.copy_directory(
            source_dir=self._generator_directory / "support_lib" / "src",
            target_dir=self.marshal.source_path()
        )
        root = Path(__file__).parent
        self._file_writer.copy_directory(
            source_dir=root / "support_lib" / "include",
            target_dir=self.marshal.source_path()
        )
        self._file_writer.copy_directory(
            source_dir=root / "support_lib" / "src",
            target_dir=self.marshal.source_path()
        )

    def generate(self, ast: list[BaseType]):
        if self.marshal.config:
            self.generate_support_lib()
            for type_def in ast:
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
