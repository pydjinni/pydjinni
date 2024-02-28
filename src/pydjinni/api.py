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

from __future__ import annotations

import json
from functools import cached_property
from importlib.metadata import entry_points, EntryPoint
from pathlib import Path
from typing import Any

from pydjinni.builder.build_config import BuildBaseConfig
from pydjinni.file.processed_files_model_builder import ProcessedFilesModelBuilder, ProcessedFiles
from pydjinni.packaging.architecture import Architecture
from pydjinni.packaging.packaging_config import PackageBaseConfig
from pydjinni.packaging.target import PackageTarget
from pydjinni.parser.parser import Parser

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # Fallback for Python < 3.11

import pydantic
import yaml
from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import FileNotFoundException, ConfigurationException, UnknownTargetException
from pydjinni.generator.external_types import ExternalTypesBuilder
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.generator.generate_config import GenerateBaseConfig
from pydjinni.generator.target import Target
from pydjinni.builder.target import BuildTarget
from pydjinni.parser.base_models import BaseType, BaseExternalType, TypeReference
from pydjinni.position import Position
from pydjinni.parser.resolver import Resolver
from pydjinni.parser.type_model_builder import TypeModelBuilder


def combine_into(d: dict, combined: dict) -> None:
    for k, v in d.items():
        if isinstance(v, dict):
            combine_into(v, combined.setdefault(k, {}))
        else:
            combined[k] = v


def get_config(config: Any, key: str, base_path: str = None) -> Any:
    """
    Tries to get an attribute from a given config model by the name of the key with `getattr`.
    If known, a base path should be provided, which helps to improve the error message by specifying in which location
    in the config file the key is missing.

    Args:
        config: the config model that he key should be read from
        key: the key that should be searched in the config model
        base_path: the base path to the key
    Returns:
        the model behind the given key, if it does exist
    Raises:
        ConfigurationException: if the given key cannot be found.
    """
    if config is not None and hasattr(config, key) and getattr(config, key) is not None:
        return getattr(config, key)
    else:
        raise ConfigurationException(f"Missing configuration for '{'.'.join([base_path, key]) if base_path else key}'")


class API:
    """
    PyDjinni has a powerful API that can be used to control the code generation directly from Python:

    ```python
    from pydjinni import API

    API().configure("pydjinni.yaml").parse("test.djinni").generate("cpp").generate("java").write_processed_files()
    ```

    is equivalent to running the CLI command:

    ```shell
    pydjinni generate test.djinni cpp java
    ```
    """

    def __init__(self):
        self._file_reader_writer = FileReaderWriter()
        self._config_model_builder = ConfigModelBuilder()
        self._external_type_model_builder = TypeModelBuilder(BaseExternalType)
        self._processed_files_model_builder = ProcessedFilesModelBuilder()
        # initializing plugins
        self._generate_targets = [self._init_generator_plugin(plugin) for plugin in
                                  entry_points(group='pydjinni.generator')]
        self._build_targets = [self._init_build_plugin(plugin) for plugin in
                               entry_points(group='pydjinni.builder')]
        self._package_targets = [self._init_package_plugin(plugin) for plugin in
                                 entry_points(group='pydjinni.packaging')]

        # generate models
        self._configuration_model = self._config_model_builder.build()
        self._external_type_model = self._external_type_model_builder.build()
        self._processed_files_model = self._processed_files_model_builder.build()
        self._file_reader_writer.setup(self._processed_files_model)
        self._external_types_builder = ExternalTypesBuilder(self._external_type_model)

    @property
    def configuration_model(self) -> type[BaseModel]:
        """
        The configuration model is assembled dynamically depending on the loaded plugins.

        Returns:
            the `pydantic` model that defines the required configuration structure.
        """
        return self._configuration_model

    @property
    def external_type_model(self) -> type[BaseExternalType]:
        """
        The type model is assembled dynamically depending on the loaded plugins.

        Returns:
            The `pydantic` model that defines the required datastructure for external types.
        """
        return self._external_type_model

    @property
    def processed_files_model(self) -> type[ProcessedFiles]:
        """
        The model for the processed files output is assembled dynamically depending on the loaded plugins.

        Returns:
            The `pydantic` model that defines the datastructure that will be generated by PyDjinni.
        """
        return self._processed_files_model

    @cached_property
    def generation_targets(self) -> dict[str, Target]:
        """
        Caution:
            The returned `Target` types are not considered part of the stable public API. Internals may change with any
            release.
        Returns:
            dictionary of all available generator targets.
        """
        return {target.key: target for target in self._generate_targets}

    @cached_property
    def package_targets(self) -> dict[str, PackageTarget]:
        return {target.key: target for target in self._package_targets}

    @cached_property
    def build_targets(self) -> dict[str, BuildTarget]:
        return {target.key: target for target in self._build_targets}

    @cached_property
    def internal_types(self) -> list:
        """
        Returns:
            A list of all pre-defined types that are available to use in the IDL.
        """
        for target in self._generate_targets:
            target.register_external_types(self._external_types_builder)
        return self._external_types_builder.build()

    def _init_generator_plugin(self, plugin: EntryPoint) -> Target:
        return plugin.load()(
            file_reader_writer=self._file_reader_writer,
            config_model_builder=self._config_model_builder,
            external_type_model_builder=self._external_type_model_builder,
            processed_files_model_builder=self._processed_files_model_builder
        )

    def _init_build_plugin(self, plugin: EntryPoint) -> BuildTarget:
        return plugin.load()(
            config_model_builder=self._config_model_builder,
        )

    def _init_package_plugin(self, plugin: EntryPoint) -> PackageTarget:
        return plugin.load()(
            config_model_builder=self._config_model_builder
        )

    def configure(self, path: Path | str = None, options: dict = None) -> ConfiguredContext:
        """
        Parses the configuration input.

        Args:
            path: the path to a configuration file.
            options: a dict with additional configuration parameters.

        Returns:
            configured API context

        Raises:
            ConfigurationException: if parsing the configuration has failed
        """

        if options is None:
            options = dict()
        if isinstance(path, str):
            path = Path(path)
        if not path and not options:
            raise ConfigurationException("Provide either a config file or a list of configuration options!")
        try:
            if path:
                with open(path, "rb") as file:
                    match path.suffix:
                        case '.yaml' | '.yml':
                            try:
                                config_dict = yaml.safe_load(file)
                            except yaml.MarkedYAMLError as e:
                                raise ConfigurationException.from_yaml_error(e)
                        case '.json':
                            try:
                                config_dict = json.load(file)
                            except json.JSONDecodeError as e:
                                raise ConfigurationException.from_json_error(path, e)
                        case '.toml':
                            try:
                                config_dict = tomllib.load(file)
                            except tomllib.TOMLDecodeError as e:
                                raise ConfigurationException(e, position=Position(file=path))
                        case _:
                            raise ConfigurationException(f"Unknown configuration file extension: '{path.suffix}'")
            else:
                config_dict = dict()
            combine_into(options, config_dict)
            config = self._configuration_model.model_validate(config_dict)
            return API.ConfiguredContext(
                config=config,
                external_types_model=self.external_type_model,
                generate_targets=self.generation_targets,
                package_targets=self.package_targets,
                build_targets=self.build_targets,
                file_reader_writer=self._file_reader_writer
            )
        except pydantic.ValidationError as e:
            raise ConfigurationException.from_pydantic_error(e)
        except FileNotFoundError:
            raise FileNotFoundException(path)

    class ConfiguredContext:
        def __init__(self, config: BaseModel, external_types_model: type[BaseExternalType],
                     generate_targets: dict[str, Target],
                     package_targets: dict[str, PackageTarget],
                     build_targets: dict[str, BuildTarget], file_reader_writer: FileReaderWriter):
            self._config = config
            self._external_types_builder = ExternalTypesBuilder(external_types_model)
            self._generate_targets = generate_targets
            self._package_targets = package_targets
            self._build_targets = build_targets
            self._resolver = Resolver(external_types_model)
            self._file_reader_writer = file_reader_writer

        @property
        def config(self) -> BaseModel:
            """
            Returns:
                The configuration model instance that is used for further processing
            """
            return self._config

        def parse(self, idl: Path | str) -> GenerateContext:
            """
            Parses the given IDL into an Abstract Syntax tree. Does not generate any file output.
            Args:
                idl: Path to the IDL file that should be processed.

            Returns:
                context that can be used to generate output
            Raises:
                FileNotFoundException            : When the given idl file does not exist.
                IdlParser.ParsingException       : When the input could not be parsed.
                IdlParser.TypeResolvingException : When a referenced type cannot be found.
                IdlParser.DuplicateTypeException : When a type is re-declared.
                IdlParser.MarshalException       : When an error happened during marshalling.
            """
            if isinstance(idl, str):
                idl = Path(idl)
            generate_config: GenerateBaseConfig = self._config.generate
            generate_targets: list[str] = list(generate_config.model_fields_set) if generate_config else []
            targets: list[Target] = [target for key, target in self._generate_targets.items() if
                                     key in generate_targets]

            for target in targets:
                target.register_external_types(self._external_types_builder)
                target.configure(generate_config)

            self._resolver.registry = dict()
            for external_type_def in self._external_types_builder.build():
                self._resolver.register_external(external_type_def)

            parser = Parser(
                resolver=self._resolver,
                targets=targets,
                supported_target_keys=list(self._generate_targets.keys()),
                file_reader=self._file_reader_writer,
                include_dirs=generate_config.include_dirs,
                default_deriving=set(generate_config.default_deriving),
                idl=idl
            )

            # parsing the input IDL. The output is an AST that contains type definitions for each provided marshal
            ast, refs = parser.parse()

            return API.ConfiguredContext.GenerateContext(
                generate_targets=self._generate_targets,
                file_writer=self._file_reader_writer,
                ast=ast,
                refs=refs,
                config=generate_config
            )

        def package(self, target: str, configuration: str = None) -> PackageContext:
            """
            configure a context for package configuration

            Returns:
                PackageContext: the packaging context
            """

            package_config: PackageBaseConfig = get_config(self._config, "package")
            if configuration:
                package_config.configuration = configuration
            package_target = self._package_targets.get(target)
            if package_target:
                build_config: BuildBaseConfig = get_config(self._config.build, package_config.build_strategy,
                                                           "build")
                build_strategy = self._build_targets[package_config.build_strategy]
                build_strategy.configure(build_config)

                package_target.configure(package_config)

                return API.ConfiguredContext.PackageContext(
                    target=package_target,
                    build_strategy=build_strategy
                )
            else:
                raise UnknownTargetException(target)

        def publish(self, target: str, configuration: str = None):
            """
            Publish a previously packaged artifact to an online repository.
            Depending on the type of package, the repository might vary. This command aims to provide a top-level
            API to publishing packages no matter what the underlying technology is.

            Args:
                target: the package type that should be published
                configuration: the configuration that should be used
            Raises:
                UnknownTargetException if the given target is not known to the system

            """
            package_config: PackageBaseConfig = self._config.package
            if configuration:
                package_config.configuration = configuration
            package_target = self._package_targets.get(target)
            if package_target:
                package_target.configure(package_config)
                package_target.publish()
            else:
                raise UnknownTargetException(target)

        class PackageContext:
            def __init__(self, target: PackageTarget, build_strategy: BuildTarget):
                self._target = target
                self._build_strategy = build_strategy

            def build(self, target: str, architectures: set[Architecture] = None,
                      clean: bool = False) -> API.ConfiguredContext.PackageContext:
                """
                Build the library for a given platform target.

                Args:
                    target:         the platform that the library should be built for. Must be supported by the package plugin
                    architectures:  list of architectures that the library should be compiled for. Overrides the
                                    architectures defined in the configuration.
                    clean:          If `True`, a clean build is preformed, meaning that the build directory is deleted
                                    and the build is started from scratch.
                Returns:
                    the current context.
                """
                self._target.build(self._build_strategy, target, architectures, clean)
                return self

            def write_package(self, clean: bool = False) -> Path:
                """
                combines all binaries previously built with `build()` into a package artifact.

                Args:
                    clean: if `True`, the packaging is done from scratch, deleting the package source directory
                           and building it from scratch.
                Returns:
                    Path to the final package that has been created
                """
                return self._target.package(clean=clean)

        class GenerateContext:
            def __init__(self, generate_targets: dict[str, Target],
                         file_writer: FileReaderWriter, ast: list[BaseType], refs: list[TypeReference],
                         config: GenerateBaseConfig):
                self._generate_targets = generate_targets
                self._file_reader_writer = file_writer
                self.ast = ast
                self.refs = refs
                self._config = config

            def generate(self, target_name: str, clean: bool = False) -> API.ConfiguredContext.GenerateContext:
                """
                generate output for a specified target based on the previously parsed IDL.
                Args:
                    target_name: name (key) of the target.
                    clean: if set to `True`, all output directories are purged before generating output, to make sure
                           that no leftovers from previous executions are still present.

                Returns:
                    the same context. Generation commands can be chained.
                """
                target = self._generate_targets[target_name]
                target.generate(self.ast, clean=clean, copy_support_lib_sources=self._config.support_lib_sources)
                return self

            def write_processed_files(self) -> Path | None:
                """
                write the file that lists all generated files to the path specified in the configuration.
                If no path is configured, this does nothing.
                Returns:
                    Path to the written file.
                """
                if self._config and self._config.list_processed_files:
                    self._file_reader_writer.write_processed_files(self._config.list_processed_files)
                    return self._config.list_processed_files
