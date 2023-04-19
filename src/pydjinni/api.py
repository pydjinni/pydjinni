from __future__ import annotations

from collections import defaultdict
from logging import Logger
from pathlib import Path

import pydantic
import yaml
from pydantic import BaseModel
from importlib.metadata import entry_points, EntryPoint

from pydjinni.config.config_model_factory import ConfigModelFactory
from pydjinni.generator.generate_config import GenerateBaseConfig
from pydjinni.exceptions import ParsingException
from pydjinni.generator.file_writer import FileWriter
from pydjinni.generator.external_types import ExternalTypesFactory
from pydjinni.generator.marshal import Marshal
from pydjinni.generator.target import Target
from pydjinni.parser.parser import IdlParser
from pydjinni.parser.resolver import Resolver
from pydjinni.parser.type_model_factory import TypeModelFactory
from pydjinni.parser.base_models import BaseType, BaseExternalType


class API:
    """
    PyDjinni has a powerful API that can be used to control the code generation directly from Python:

    ```python
    from pydjinni import API

    API().configure().parse("test.djinni").generate("cpp").generate("java")
    ```

    is equivalent to running the CLI command:

    ```shell
    pydjinni generate test.djinni cpp java
    ```
    """

    def __init__(self, logger: Logger):
        self._file_writer = FileWriter()
        self._config_factory = ConfigModelFactory()
        self._external_type_model_factory = TypeModelFactory(BaseExternalType)
        self._logger = logger
        # initializing plugins
        generator_plugins = entry_points(group='pydjinni.generator')
        self._generate_targets = [self._init_generator_plugin(plugin) for plugin in generator_plugins]

        # generate models
        self._configuration_model = self._config_factory.build()
        self._external_type_model = self._external_type_model_factory.build()
        self._external_types_factory = ExternalTypesFactory(self._external_type_model)

    @property
    def configuration_model(self) -> type[BaseModel]:
        """
        The configuration model is assembled dynamically depending on the loaded plugins.

        Returns:
            the `pydantic` model that defines the required configuration structure.
        """
        return self._configuration_model

    @property
    def external_type_model(self) -> type[BaseModel]:
        """
        The type model is assembled dynamically depending on the loaded plugins.

        Returns:
            The `pydantic` model that defines the required datastructure for external types.
        """
        return self._external_type_model

    @property
    def generation_targets(self) -> dict[str, Target]:
        """
        Caution:
            The returned `Target` types are not considered part of the stable public API. Internals may change with any
            release.
        Returns:
            dictionary of all available generator targets.
        """
        return {target.key: target for target in self._generate_targets}

    @property
    def internal_types(self) -> list:
        """
        Returns:
            A list of all pre-defined types that are available to use in the IDL.
        """
        for target in self._generate_targets:
            for marshal in target.marshals:
                marshal.register_external_types(self._external_types_factory)
        return self._external_types_factory.build()


    def _init_generator_plugin(self, plugin: EntryPoint) -> Target:
        target_type: type[Target] = plugin.load()
        return target_type(
            file_writer=self._file_writer,
            config_factory=self._config_factory,
            external_type_model_factory=self._external_type_model_factory,
            logger=self._logger
        )

    def configure(self, path: Path = Path("pydjinni.yaml"), options: tuple[str] = ()) -> ConfiguredContext:
        """
        Parses the configuration input.

        Returns:
            configured API context
        """

        def _parse_option(option: str) -> dict:
            key_list, value = option.split('=', 1)
            keys = key_list.split('.')
            result = defaultdict()
            d = result
            for subkey in keys[:-1]:
                d = d.setdefault(subkey, {})
            d[keys[-1]] = value
            return result

        def _combine_into(d: dict, combined: dict) -> None:
            for k, v in d.items():
                if isinstance(v, dict):
                    _combine_into(v, combined.setdefault(k, {}))
                else:
                    combined[k] = v

        try:
            config_dict = yaml.safe_load(path.read_text())
            for option in options:
                _combine_into(_parse_option(option), config_dict)
            config = self._configuration_model.parse_obj(config_dict)
            return API.ConfiguredContext(
                logger=self._logger,
                config=config,
                external_types_model=self.external_type_model,
                generate_targets=self.generation_targets,
                file_writer=self._file_writer
            )
        except pydantic.ValidationError as e:
            raise ParsingException(e)

    class ConfiguredContext:
        def __init__(self, logger: Logger, config: BaseModel, external_types_model: type[BaseModel], generate_targets: dict[str, Target], file_writer: FileWriter):
            self._logger = logger
            self._config = config
            self._external_types_factory = ExternalTypesFactory(external_types_model)
            self._generate_targets = generate_targets
            self._resolver = Resolver(logger=self._logger)
            self._file_writer = file_writer

        def parse(self, idl: Path) -> GenerateContext:
            """
            Parses the given IDL into an Abstract Syntax tree. Does not generate any file output.
            Args:
                idl: Path to the IDL file that should be processed.

            Returns:
                context that can be used to generate output
            """
            generate_config: GenerateBaseConfig = self._config.generate
            if generate_config is not None:
                # only marshals that are configured are passed to the parser
                generate_targets: list[str] = list(generate_config.model_fields_set)
            else:
                generate_targets = []
            marshals: list[Marshal] = []
            for key, target in self._generate_targets.items():
                if key in generate_targets:
                    marshals += target.marshals

            for marshal in marshals:
                marshal.register_external_types(self._external_types_factory)
                marshal.configure(generate_config)

            for external_type_def in self._external_types_factory.build():
                self._resolver.register_external(external_type_def)

            parser = IdlParser(
                logger=self._logger,
                resolver=self._resolver,
                marshals=marshals
            )

            # parsing the input IDL. The output is an AST that contains type definitions for each provided marshal
            ast = parser.parse(idl)
            return API.ConfiguredContext.GenerateContext(
                generate_targets=self._generate_targets,
                file_writer=self._file_writer,
                ast=ast,
                config=generate_config
            )

        class GenerateContext:
            def __init__(self, generate_targets: dict[str, Target], file_writer: FileWriter, ast: list[BaseType], config: GenerateBaseConfig):
                self._generate_targets = generate_targets
                self._file_writer = file_writer
                self._ast = ast
                self._config = config

            def generate(self, target_name: str) -> API.ConfiguredContext.GenerateContext:
                """
                generate output for a specified target based on the previously parsed IDL.
                Args:
                    target_name: name of the target.

                Returns:
                    the same context. Generation commands can be chained.
                """
                target = self._generate_targets[target_name]
                for type_def in self._ast:
                    target.generate(type_def)
                return self

            def write_out_files(self) -> API.ConfiguredContext.GenerateContext:
                """
                write the file that lists all generated files to the path specified in the configuration.
                If no path is configured, this does nothing.
                Returns:
                    the same context.
                """
                if self._config.list_out_files is not None:
                    self._file_writer.write_generated_files(self._config.list_out_files)
                return self
