from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, get_args

import pydantic
from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.config.types import OutPaths, IdentifierStyle
from pydjinni.exceptions import ConfigurationException, ApplicationException
from pydjinni.generator.external_types import ExternalTypesBuilder
from pydjinni.parser.ast import Record, Interface, Enum, Flags
from pydjinni.parser.base_models import BaseType, BaseField
from pydjinni.parser.type_model_builder import TypeModelBuilder

ConfigModel = TypeVar("ConfigModel", bound=BaseModel)
ExternalTypeDef = TypeVar("ExternalTypeDef", bound=BaseModel)

class Marshal(ABC, Generic[ConfigModel, ExternalTypeDef]):
    """
    Abstract class for defining a Marshal class. The purpose of marshalling is to transform a given input to the
    required, use-case specific output, based on domain specific knowledge and the configuration by the user.

    Methods defined in the Marshal are supposed to be called from the Jinja template that renders the output.
    """

    class MarshalException(ApplicationException, code=160):
        def __init__(self, input_def: BaseType | BaseField, message: str):
            super().__init__(message)
            self.input_def = input_def

    def __init_subclass__(cls, types: dict[str, ExternalTypeDef]) -> None:
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
        self.config = config

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

    def marshal_namespace(
            self,
            type_def: BaseType,
            identifier_style: IdentifierStyle | IdentifierStyle.Case,
            config_namespace: str = None,
            separator: str = "::"
    ) -> list[str]:
        namespace = [namespace.convert(identifier_style) for namespace in type_def.namespace]
        if config_namespace:
            namespace = config_namespace.split(separator) + namespace
        return namespace

    @abstractmethod
    def marshal_type(self, type_def: BaseType):
        raise NotImplementedError

    @abstractmethod
    def marshal_field(self, field_def: BaseField):
        raise NotImplementedError

    def marshal(self, type_def: BaseType):
        if self.config:
            try:
                self.marshal_type(type_def)
                match type_def:
                    case Record():
                        for field_def in type_def.fields:
                            self.marshal_field(field_def)
                        for constant in type_def.constants:
                            self.marshal_field(constant)
                    case Interface():
                        for method in type_def.methods:
                            self.marshal_field(method)
                            for parameter in method.parameters:
                                self.marshal_field(parameter)
                        for property_def in type_def.properties:
                            self.marshal_field(property_def)
                        for constant in type_def.constants:
                            self.marshal_field(constant)
                    case Enum():
                        for item in type_def.items:
                            self.marshal_field(item)
                    case Flags():
                        for flag in type_def.flags:
                            self.marshal_field(flag)
            except pydantic.ValidationError as e:
                raise Marshal.MarshalException(type_def, str(e))
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")
