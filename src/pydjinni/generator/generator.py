import inspect
import re
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

from jinja2 import Environment, FileSystemLoader

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import ConfigurationException, ApplicationException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFilesModelBuilder
from pydjinni.parser.type_model_builder import TypeModelBuilder
from .marshal import Marshal
from pydjinni.config.types import OutPaths
from pydjinni.parser.base_models import BaseExternalType, BaseType


class Generator(ABC):
    """
    Abstract class for defining generators. Each generator can utilize one or more Marshal classes, specified as
    generic arguments.
    """

    class GenerationException(ApplicationException, code=160):
        """Generation error"""

        def __init__(self, input_def: BaseType, message: str):
            super().__init__(message)
            self.input_def = input_def

    def __init_subclass__(
            cls,
            key: str,
            marshal: type[Marshal],
            writes_header: bool = False,
            writes_source: bool = False,
            support_lib_commons: bool = False,
            filters: list[Callable] = None,
            tests: list[Callable] = None) -> None:
        cls._marshal_type = marshal
        cls.key = key
        cls.writes_header = writes_header
        cls.writes_source = writes_source
        cls.support_lib_commons = support_lib_commons
        cls.filters = filters or []
        cls.tests = tests or []

    def __init__(
            self,
            file_writer: FileReaderWriter,
            config_model_builder: ConfigModelBuilder,
            external_type_model_builder: TypeModelBuilder,
            processed_files_model_builder: ProcessedFilesModelBuilder):
        self._file_writer = file_writer
        self._input_file = None
        self._generator_directory = Path(inspect.getfile(self.__class__)).parent

        self._jinja_env = Environment(
            loader=FileSystemLoader(self._generator_directory / "templates"),
            trim_blocks=True, lstrip_blocks=True,
            keep_trailing_newline=True
        )
        for filter_callable in self.filters:
            self._jinja_env.filters[filter_callable.__name__] = filter_callable
        for test_callable in self.tests:
            self._jinja_env.tests[test_callable.__name__] = test_callable
        processed_files_model_builder.add_generated_field(self.key, header=self.writes_header,
                                                          source=self.writes_source)
        self.marshal = self._marshal_type(
            key=self.key,
            config_model_builder=config_model_builder,
            external_type_model_builder=external_type_model_builder
        )

    @property
    def header_path(self) -> Path:
        """
        Returns:
             the path where generated header files should be written.
        """
        out = self.marshal.config.out
        if type(out) is OutPaths:
            return out.header
        else:
            return out

    @property
    def source_path(self) -> Path:
        """
        Returns:
             the path where generated source files should be written
        """
        out = self.marshal.config.out
        if type(out) is OutPaths:
            return out.source
        else:
            return out

    def write_header(self, template: str, filename: Path = None, **kwargs):
        assert self.writes_header, "Should only be called on generators that do produce header files"
        assert kwargs.get('type_def') or filename, "If no type_def is given, an explicit filename must be provided"
        if kwargs.get('type_def') and filename is None:
            filename = getattr(kwargs['type_def'], self.key).header
        self._file_writer.write_header(
            key=self.key,
            filename=self.header_path / filename,
            content=self._jinja_env.get_template(template).render(
                config=self.marshal.config,
                input_file=self._input_file,
                **kwargs
            )
        )

    def write_source(self, template: str, filename: Path = None, **kwargs):
        assert self.writes_source, "Should only be called on generators that do produce source files"
        assert kwargs.get('type_def') or filename, "If no type_def is given, an explicit filename must be provided"
        if kwargs.get('type_def') and filename is None:
            filename = getattr(kwargs['type_def'], self.key).source
        self._file_writer.write_source(
            key=self.key,
            filename=self.source_path / filename,
            content=self._jinja_env.get_template(template).render(
                config=self.marshal.config,
                input_file=self._input_file,
                **kwargs
            )
        )

    def input_file(self, path: Path):
        """Sets the input file that is currently being processed."""
        self._input_file = path

    def generate_support_lib(self):
        """
        Copies support lib files if they exist. Fails silently if no files can be found in the expected directories.
        """
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=self._generator_directory / "support_lib" / "include",
            target_dir=self.source_path
        )
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=self._generator_directory / "support_lib" / "src",
            target_dir=self.source_path
        )
        root = Path(__file__).parent
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=root / "support_lib" / "include",
            target_dir=self.source_path
        )
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=root / "support_lib" / "src",
            target_dir=self.source_path
        )

    def clean(self):
        """purge all content from source and header output directories"""
        shutil.rmtree(self.header_path, ignore_errors=True)
        shutil.rmtree(self.source_path, ignore_errors=True)

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        def call_generate_method(definition: BaseType):
            def traverse_hierarchy(def_class, definition):
                if def_class == BaseExternalType:
                    raise Generator.GenerationException(
                        definition,
                        f"The generator '{self.key}' does not support the type '{definition.__class__.__qualname__}'"
                    )
                qualifier = '_'.join([word.lower() for word in re.findall(r'[A-Z][a-z0-9]*', def_class.__qualname__)])
                method_name = f"generate_{qualifier}"
                if hasattr(self, method_name):
                    getattr(self, method_name)(definition)
                else:
                    for base in def_class.__bases__:
                        traverse_hierarchy(base, definition)

            traverse_hierarchy(definition.__class__, definition)

        if self.marshal.config:
            if self.writes_header:
                self._file_writer.setup_include_dir(self.key, self.header_path)
            if self.writes_source:
                self._file_writer.setup_source_dir(self.key, self.source_path)
            if self.support_lib_commons and copy_support_lib_sources:
                self.generate_support_lib()
            for type_def in ast:
                call_generate_method(type_def)
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")
