# Copyright 2023 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import re
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, TypeVar

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.config.types import OutPaths
from pydjinni.exceptions import ConfigurationException, ApplicationException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFilesModelBuilder
from pydjinni.parser.base_models import BaseExternalType, BaseType, BaseField
from pydjinni.parser.type_model_builder import TypeModelBuilder
from .external_types import ExternalTypesBuilder

ConfigModel = TypeVar("ConfigModel", bound=BaseModel)
ExternalTypeModel = TypeVar("ExternalTypeModel", bound=BaseModel)


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

    @property
    @abstractmethod
    def key(self) -> str:
        """
        The name of the generator. Will be used as configuration key and for importing/exporting external types.

        Typically, a target will have one generator with the same name (key) as the target.
        If additional glue code in C++ is provided, this will usually require a separate generator with a distinct name.
        """
        pass

    @property
    @abstractmethod
    def config_model(self) -> type[ConfigModel]:
        """
        The Pydantic model that defines the configuration options for the generator.

        The model will automatically be registered in the system and is then available in the documentation and as part
        of the  JSON-Schema for the configuration file.
        """
        pass

    @property
    def external_type_model(self) -> type[ExternalTypeModel] | None:
        """
        The Pydantic model of the external type specification for the generator. The model should contain all
        information that is required to reference and use an external type in the generated code.

        The model will automatically be registered in the system and is then available in the documentation and as part
        of the JSON-Schema for external types.
        """
        return None

    @property
    def external_types(self) -> dict[str, ExternalTypeModel]:
        """
        A dictionary of all builtin types that are supported by the generator.
        If the list is incomplete, an error is thrown when the user tries to use an unsupported type in a project that
        uses the generator.

        A complete list of all builtin types can be found in `pydjinni/generator/external_types.py`
        """
        return {}

    @property
    def marshal_models(self) -> dict[type, type]:
        """
        A mapping of AST types to the marshalling model required by the generator.
        For each type in the AST, the generator searches for a matching marshalling model in this dictionary.
        If no marshalling model is found, an error will be thrown suggesting that the given AST type is not supported
        by the generator.

        The generator will search for a matching marshalling model by traversing the type hierarchy of the AST type until
        a matching marshalling model is found.

        A marshalling model must be a Pydantic model with two fields:
        - `decl` for the type of field declaration and
        - `config` for the generator configuration

        All marshalling must happen in methods decorated as `@cached_property`, where the declaration and the
        configuration is used to derive information needed by the generator.
        Type marshalling properties must at least contain a property for each field in the given external type model.
        Every property that should be exported as part of the external type YAML definition must be decorated with
        `@computed_field`.
        """
        return {}

    @property
    def writes_header(self) -> bool:
        """
        Whether the generator will generate header files. This information is required for documentation purposes and
        for providing a valid JSON-Schema for the processed files report.
        """
        return False

    @property
    def writes_source(self) -> bool:
        """
        Whether the generator will generate source files. This information is required for documentation purposes and
        for providing a valid JSON-Schema for the processed files report.
        """
        return False

    @property
    def support_lib_commons(self) -> bool:
        """
        Whether the code generated by this generator depends on the common support lib code provided by pydjinni.
        """
        return False

    @property
    def filters(self) -> list[Callable]:
        """
        Jinja2 filter functions that are required in the generators Jinja templates
        """
        return []

    @property
    def tests(self) -> list[Callable]:
        """
        Jinja2 test functions that are required in the generators Jinja templates
        """
        return []

    def __init__(
            self,
            file_writer: FileReaderWriter,
            config_model_builder: ConfigModelBuilder,
            external_type_model_builder: TypeModelBuilder,
            processed_files_model_builder: ProcessedFilesModelBuilder):
        self._file_writer = file_writer
        self._generator_directory = Path(inspect.getfile(self.__class__)).parent
        self.config: ConfigModel | None = None

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
        config_model_builder.add_generator_config(self.key, self.config_model)
        if self.external_type_model:
            external_type_model_builder.add_field(self.key, self.external_type_model)

    def register_external_types(self, external_types_factory: ExternalTypesBuilder):
        if self.external_types:
            external_types_factory.register(self.key, self.external_types)

    def configure(self, config: ConfigModel):
        self.config = config
        if self.writes_header:
            self._file_writer.setup_include_dir(self.key, self.header_path)
        if self.writes_source:
            self._file_writer.setup_source_dir(self.key, self.source_path)

    @property
    def header_path(self) -> Path:
        """
        The path where generated header files should be written.

        The default implementation expects the generators config model to contain a field `out` that is either a Path
        or of type `OutPaths`.

        Override this if the generators config doesn't match with those expectations.
        """
        out = self.config.out
        if type(out) is OutPaths:
            return out.header
        else:
            return out

    @property
    def source_path(self) -> Path:
        """
        The path where generated source files should be written.

        The default implementation expects the generators config model to contain a field `out` that is either a Path
        or of type `OutPaths`.

        Override this if the generators config doesn't match with those expectations.
        """
        out = self.config.out
        if type(out) is OutPaths:
            return out.source
        else:
            return out

    def write_header(self, template: str, filename: Path = None, **kwargs):
        """
        Method that must be used for any header file that is written by the generator.

        Providing a filename is optional if a type definition is provided in the `type_def` parameter. In this case the
        filename can be derived from the marshalling model, given that a `header` field is provided.
        """
        assert self.writes_header, "Should only be called on generators that do produce header files"
        assert kwargs.get('type_def') or filename, "If no type_def is given, an explicit filename must be provided"
        if kwargs.get('type_def') and filename is None:
            filename = getattr(kwargs['type_def'], self.key).header
        self._file_writer.write_header(
            key=self.key,
            filename=self.header_path / filename,
            content=self._jinja_env.get_template(template).render(
                config=self.config,
                **kwargs
            )
        )

    def write_source(self, template: str, filename: Path = None, **kwargs):
        """
        Method that must be used for any source file that is written by the generator.

        Providing a filename is optional if a type definition is provided in the `type_def` parameter. In this case the
        filename can be derived from the marshalling model, given that a `source` field is provided.
        """
        assert self.writes_source, "Should only be called on generators that do produce source files"
        assert kwargs.get('type_def') or filename, "If no type_def is given, an explicit filename must be provided"
        if kwargs.get('type_def') and filename is None:
            filename = getattr(kwargs['type_def'], self.key).source
        self._file_writer.write_source(
            key=self.key,
            filename=self.source_path / filename,
            content=self._jinja_env.get_template(template).render(
                config=self.config,
                **kwargs
            )
        )

    def generate_support_lib(self):
        """
        Copies support lib files if they exist. Fails silently if no files can be found in the expected directories.
        """
        self._file_writer.copy_header_directory(
            key=self.key,
            header_dir=self._generator_directory / "support_lib" / "include",
            target_dir=self.header_path
        )
        self._file_writer.copy_source_directory(
            key=self.key,
            source_dir=self._generator_directory / "support_lib" / "src",
            target_dir=self.source_path
        )
        if self.support_lib_commons:
            root = Path(__file__).parent
            self._file_writer.copy_header_directory(
                key=self.key,
                header_dir=root / "support_lib" / "include",
                target_dir=self.header_path
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
        """
        This method is initiated by the system to start code generation.

        Iterates over all given type definitions and dynamically searches for a matching generator function.
        A valid generator function must have the following signature, where `<type>` is a lowercase representation of
        the full type name, separated by `_` instead of `.` if the given type is a subclass:
        ```py
        def generate_<type>(self, type_def: BaseType):
            ...
        ```

        If no direct match for the types class name can be found, the inheritance hierarchy is traversed until a match
        was found.

        Examples:
            - `def generate_interface(self, type_def: Interface)` will match for the `Interface` type.
            - `def generate_base_type(self, type_def: BaseType)` will match for all types deriving from `BaseType`
              if no better match can be found.

        This method may be overridden if the default dynamic detection behaviour doesn't fit the requirements.
        """

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

        if self.config:
            if copy_support_lib_sources:
                self.generate_support_lib()
            for type_def in ast:
                call_generate_method(type_def)
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")

    def marshal(self, type_decls: list[BaseType], field_decls: list[BaseField]):
        """
        Attaches marshalling models to the provided type and field definitions.

        Searches the provided marshalling model mappings for a matching marshalling model for each given type or field.
        If no direct match can be found, the inheritance hierarchy is traversed until a matching model is found.

        Once a matching marshalling model was found, it is initialized and attached to the given type/field definition.

        Note:
            During attachment of the marshalling models, no actual marshalling is happening. Only during rendering of
            the Jinja templates the marshalling model properties are evaluated.

        The method may be overriden with custom marshalling logic if the default behaviour doesn't fit the
        requirements. But the outcome must always be a Pydantic model being attached to each given type and field
        declaration passed to the method!
        """

        def traverse_hierarchy(def_class, definition):
            if def_class in [BaseExternalType, BaseModel]:
                raise Generator.GenerationException(
                    definition,
                    f"Language feature '{definition.__class__.__qualname__}' is not supported for the target '{self.key}'"
                )
            if self.marshal_models.get(def_class):
                definition.__setattr__(self.key, self.marshal_models[def_class](decl=definition, config=self.config))
            else:
                for base in def_class.__bases__:
                    traverse_hierarchy(base, definition)

        if self.config:
            if self.marshal_models:
                for definitions in [type_decls, field_decls]:
                    for definition in definitions:
                        traverse_hierarchy(type(definition), definition)
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")
