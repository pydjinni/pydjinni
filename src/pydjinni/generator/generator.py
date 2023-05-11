import inspect
import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import ConfigurationException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFilesModelBuilder
from pydjinni.parser.ast import Flags, Enum, Record, Interface, BaseType
from pydjinni.parser.type_model_builder import TypeModelBuilder
from .marshal import Marshal


class Generator(ABC):
    """
    Abstract class for defining generators. Each generator can utilize one or more Marshal classes, specified as
    generic arguments.
    """

    def __init_subclass__(cls, key: str, marshal: type[Marshal], writes_header: bool = False,
                          writes_source: bool = False, support_lib_commons: bool = False) -> None:
        cls._marshal_type = marshal
        cls.key = key
        cls.writes_header = writes_header
        cls.writes_source = writes_source
        cls.support_lib_commons = support_lib_commons

    def __init__(
            self,
            file_writer: FileReaderWriter,
            config_model_builder: ConfigModelBuilder,
            external_type_model_builder: TypeModelBuilder,
            processed_files_model_builder: ProcessedFilesModelBuilder):
        self._file_writer = file_writer
        self._input_file = None
        self._generator_directory = Path(inspect.getfile(self.__class__)).parent

        def is_system_include(header: str):
            return str(header).startswith("<") and str(header).endswith(">")

        self._jinja_env = Environment(
            loader=FileSystemLoader(self._generator_directory / "templates"),
            trim_blocks=True, lstrip_blocks=True,
            keep_trailing_newline=True
        )
        self._jinja_env.tests["system_include"] = is_system_include
        processed_files_model_builder.add_generated_field(self.key, header=self.writes_header,
                                                          source=self.writes_source)
        self.marshal = self._marshal_type(
            key=self.key,
            config_model_builder=config_model_builder,
            external_type_model_builder=external_type_model_builder
        )

    def write_header(self, template: str, path: Path, **kwargs):
        assert self.writes_header, "Should only be called on generators that do produce header files"
        self._file_writer.write_header(
            key=self.key,
            filename=path,
            content=self._jinja_env.get_template(template).render(
                config=self.marshal.config,
                input_file=self._input_file,
                **kwargs
            )
        )

    def write_source(self, template: str, path: Path, **kwargs):
        assert self.writes_source, "Should only be called on generators that do produce source files"
        self._file_writer.write_source(
            key=self.key,
            filename=path,
            content=self._jinja_env.get_template(template).render(
                config=self.marshal.config,
                input_file=self._input_file,
                **kwargs
            )
        )

    def input_file(self, path: Path):
        """Sets the input file that is currently being processed."""
        self._input_file = path

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
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=self._generator_directory / "support_lib" / "include",
            target_dir=self.marshal.source_path()
        )
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=self._generator_directory / "support_lib" / "src",
            target_dir=self.marshal.source_path()
        )
        root = Path(__file__).parent
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=root / "support_lib" / "include",
            target_dir=self.marshal.source_path()
        )
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=root / "support_lib" / "src",
            target_dir=self.marshal.source_path()
        )

    def clean(self):
        """purge all content from source and header output directories"""
        shutil.rmtree(self.marshal.header_path(), ignore_errors=True)
        shutil.rmtree(self.marshal.source_path(), ignore_errors=True)

    def generate(self, ast: list[BaseType]):
        if self.marshal.config:
            if self.writes_header:
                self._file_writer.setup_include_dir(self.key, self.marshal.header_path())
            if self.support_lib_commons:
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
