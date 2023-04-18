from __future__ import annotations

from collections import defaultdict
from logging import Logger
from pathlib import Path

import pydantic
import yaml
from pydantic import BaseModel
from importlib.metadata import entry_points, EntryPoint

from rich.pretty import pretty_repr

from pydjinni.config.config_model_factory import ConfigModelFactory
from pydjinni.exceptions import ParsingException
from pydjinni.file_writer import FileWriter
from pydjinni.generator.external_types import ExternalTypesFactory
from pydjinni.generator.marshal import Marshal
from pydjinni.generator.target import Target
from pydjinni.parser.parser import IdlParser
from pydjinni.parser.resolver import Resolver
from pydjinni.parser.type_model_factory import TypeModelFactory
from pydjinni.parser.base_models import BaseType, BaseExternalType, BaseField


class API:
    def __init__(self, logger: Logger):
        self._file_writer = FileWriter()
        self._config_factory = ConfigModelFactory()
        self._external_type_model_factory = TypeModelFactory(BaseExternalType)
        self._logger = logger
        self._resolver = Resolver(logger=self._logger)

        # initializing plugins
        generator_plugins = entry_points(group='pydjinni.generator')
        self._generate_targets = [self._init_generator_plugin(plugin) for plugin in generator_plugins]

        # generate models
        self._configuration_model = self._config_factory.build()
        self._external_type_model = self._external_type_model_factory.build()
        self._external_types_factory = ExternalTypesFactory(self._external_type_model)

    @property
    def configuration_model(self) -> BaseModel:
        return self._configuration_model

    @property
    def external_type_model(self) -> BaseModel:
        return self._external_type_model

    @property
    def generation_targets(self) -> dict[str, Target]:
        """
        :return: list of all available generator targets
        """
        return {target.key: target for target in self._generate_targets}

    def parse(self, config: BaseModel, idl: Path) -> list[BaseType]:
        generate_config = config.generate
        if generate_config is not None:
            # only marshals that are configured are passed to the parser
            generate_targets: list[str] = list(generate_config.model_fields_set)
        else:
            generate_targets = []
        marshals: list[Marshal] = []
        for target in self._generate_targets:
            if target.key in generate_targets:
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
        return parser.parse(idl)

    def generate(self, target: Target, ast: list[BaseType]):
        for type_def in ast:
            target.generate(type_def)
        self._file_writer.write_generated_files(Path("generated-files.txt"))

    def _init_generator_plugin(self, plugin: EntryPoint) -> Target:
        target_type: type[Target] = plugin.load()
        return target_type(
            file_writer=self._file_writer,
            config_factory=self._config_factory,
            external_type_model_factory=self._external_type_model_factory,
            logger=self._logger
        )

    def _parse_option(self, option: str, option_group: str) -> dict:
        key_list, value = option.split('=', 1)
        keys = key_list.split('.')
        keys.insert(0, option_group)
        result = defaultdict()
        d = result
        for subkey in keys[:-1]:
            d = d.setdefault(subkey, {})
        d[keys[-1]] = value
        return result

    def _combine_into(self, d: dict, combined: dict) -> None:
        for k, v in d.items():
            if isinstance(v, dict):
                self._combine_into(v, combined.setdefault(k, {}))
            else:
                combined[k] = v

    def load_config(self, path: Path = Path("pydjinni.yaml"), options: tuple[str] = (), option_group: str = "") -> BaseModel:
        try:
            self._logger.debug("Loading configuration")
            config_dict = yaml.safe_load(path.read_text())
            for option in options:
                self._combine_into(self._parse_option(option, option_group), config_dict)
            self._logger.debug(pretty_repr(config_dict))
            config = self._configuration_model.parse_obj(config_dict)
            self._logger.debug(pretty_repr(config))
            return config
        except pydantic.ValidationError as e:
            raise ParsingException(e)
