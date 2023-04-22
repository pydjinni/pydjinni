from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, get_args

import pydantic
from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.config.types import OutPaths
from pydjinni.exceptions import ConfigurationException
from pydjinni.generator.external_types import ExternalTypes, ExternalTypeDef, ExternalTypesBuilder
from pydjinni.parser.base_models import BaseType, BaseField
from pydjinni.parser.type_model_builder import TypeModelBuilder

ConfigModel = TypeVar("ConfigModel", bound=BaseModel)


class Marshal(ABC, Generic[ConfigModel, ExternalTypeDef]):
    """
    Abstract class for defining a Marshal class. The purpose of marshalling is to transform a given input to the
    required, use-case specific output, based on domain specific knowledge and the configuration by the user.

    Methods defined in the Marshal are supposed to be called from the Jinja template that renders the output.
    """

    class MarshalException(Exception):
        def __init__(self, input_def: BaseType | BaseField, message: str):
            super().__init__(message)
            self.input_def = input_def

    def __init_subclass__(cls, types: ExternalTypes[ExternalTypeDef]) -> None:
        cls._config_model, cls._external_type_def = get_args(cls.__orig_bases__[0])
        cls.types = types

    def __init__(
            self,
            key: str,
            config_model_builder: ConfigModelBuilder,
            external_type_model_builder: TypeModelBuilder
    ):
        self.config: ConfigModel | None = None
        self.key = key
        config_model_builder.add_generator_config(key, self._config_model)
        external_type_model_builder.add_field(key, self._external_type_def)

    def register_external_types(self, external_types_factory: ExternalTypesBuilder):
        external_types_factory.register(self.key, self.types)

    def configure(self, config: ConfigModel):
        self.config = getattr(config, self.key)

    def header_path(self) -> Path:
        """
        :return: the path where generated header files should be written.
        """
        out = self.config.out
        if type(out) is OutPaths:
            return out.header
        else:
            return out

    def source_path(self) -> Path:
        """
        :return: the path where generated source files should be written
        """
        out = self.config.out
        if type(out) is OutPaths:
            return out.source
        else:
            return out

    @abstractmethod
    def marshal_type(self, type_def: BaseType):
        raise NotImplementedError

    @abstractmethod
    def marshal_field(self, field_def: BaseField):
        raise NotImplementedError

    def marshal(self, input_def: BaseType | BaseField):
        if self.config:
            try:
                match input_def:
                    case BaseType():
                        self.marshal_type(input_def)
                    case BaseField():
                        self.marshal_field(input_def)
            except pydantic.ValidationError as e:
                raise Marshal.MarshalException(input_def, str(e))
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")
