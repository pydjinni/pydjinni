from __future__ import annotations

from importlib.metadata import entry_points, EntryPoint
from pathlib import Path

import pydantic
import yaml
from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import FileNotFoundException, ConfigurationException
from pydjinni.generator.external_types import ExternalTypesBuilder
from pydjinni.generator.file_writer import FileWriter
from pydjinni.generator.generate_config import GenerateBaseConfig
from pydjinni.generator.marshal import Marshal
from pydjinni.generator.target import Target
from pydjinni.parser.base_models import BaseType, BaseExternalType
from pydjinni.parser.parser import IdlParser
from pydjinni.parser.resolver import Resolver
from pydjinni.parser.type_model_builder import TypeModelBuilder


def combine_into(d: dict, combined: dict) -> None:
    for k, v in d.items():
        if isinstance(v, dict):
            combine_into(v, combined.setdefault(k, {}))
        else:
            combined[k] = v


class API:
    """
    PyDjinni has a powerful API that can be used to control the code generation directly from Python:

    ```python
    from pydjinni import API

    API().configure("pydjinni.yaml").parse("test.djinni").generate("cpp").generate("java").write_out_files()
    ```

    is equivalent to running the CLI command:

    ```shell
    pydjinni generate test.djinni cpp java
    ```
    """

    def __init__(self):
        self._file_writer = FileWriter()
        self._config_model_builder = ConfigModelBuilder()
        self._external_type_model_builder = TypeModelBuilder(BaseExternalType)
        # initializing plugins
        generator_plugins = entry_points(group='pydjinni.generator')
        self._generate_targets = [self._init_generator_plugin(plugin) for plugin in generator_plugins]

        # generate models
        self._configuration_model = self._config_model_builder.build()
        self._external_type_model = self._external_type_model_builder.build()
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
                marshal.register_external_types(self._external_types_builder)
        return self._external_types_builder.build()

    def _init_generator_plugin(self, plugin: EntryPoint) -> Target:
        target_type: type[Target] = plugin.load()
        return target_type(
            file_writer=self._file_writer,
            config_model_builder=self._config_model_builder,
            external_type_model_builder=self._external_type_model_builder,
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
            config_dict = yaml.safe_load(path.read_text()) if path is not None else dict()
            combine_into(options, config_dict)
            config = self._configuration_model.model_validate(config_dict)
            return API.ConfiguredContext(
                config=config,
                external_types_model=self.external_type_model,
                generate_targets=self.generation_targets,
                file_writer=self._file_writer
            )
        except (pydantic.ValidationError, yaml.YAMLError) as e:
            raise ConfigurationException(str(e))
        except FileNotFoundError:
            raise FileNotFoundException(path)

    class ConfiguredContext:
        def __init__(self, config: BaseModel, external_types_model: type[BaseExternalType],
                     generate_targets: dict[str, Target], file_writer: FileWriter):
            self._config = config
            self._external_types_builder = ExternalTypesBuilder(external_types_model)
            self._generate_targets = generate_targets
            self._resolver = Resolver(external_types_model)
            self._file_writer = file_writer

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
            if generate_config is not None:
                # only marshals that are configured are passed to the parser
                generate_targets: list[str] = list(generate_config.model_fields_set)
            else:
                generate_targets = []
            marshals: list[Marshal] = []
            for key, target in self._generate_targets.items():
                target.input_file(idl)
                if key in generate_targets:
                    marshals += target.marshals

            for marshal in marshals:
                marshal.register_external_types(self._external_types_builder)
                marshal.configure(generate_config)

            for external_type_def in self._external_types_builder.build():
                self._resolver.register_external(external_type_def)

            parser = IdlParser(
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
            def __init__(self, generate_targets: dict[str, Target], file_writer: FileWriter, ast: list[BaseType],
                         config: GenerateBaseConfig):
                self._generate_targets = generate_targets
                self._file_writer = file_writer
                self._ast = ast
                self._config = config

            @property
            def ast(self) -> list[BaseType]:
                """
                Returns:
                    Abstract syntax tree (AST) that was generated by the parser.
                """
                return self._ast

            def generate(self, target_name: str) -> API.ConfiguredContext.GenerateContext:
                """
                generate output for a specified target based on the previously parsed IDL.
                Args:
                    target_name: name of the target.

                Returns:
                    the same context. Generation commands can be chained.
                """
                target = self._generate_targets[target_name]
                target.generate(self._ast)
                return self

            def write_out_files(self) -> API.ConfiguredContext.GenerateContext:
                """
                write the file that lists all generated files to the path specified in the configuration.
                If no path is configured, this does nothing.
                Returns:
                    the same context.
                """
                if self._config and self._config.list_out_files:
                    self._file_writer.write_generated_files(self._config.list_out_files)
                return self
