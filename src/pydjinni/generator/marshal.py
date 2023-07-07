import re
from abc import ABC
from typing import TypeVar, Generic, get_args

import pydantic
from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import ConfigurationException
from pydjinni.generator.external_types import ExternalTypesBuilder
from pydjinni.parser.ast import Record, Interface, Enum, Flags, Function, Parameter
from pydjinni.parser.base_models import BaseType, BaseField, BaseClassType, Constant, BaseExternalType
from pydjinni.parser.type_model_builder import TypeModelBuilder

ConfigModel = TypeVar("ConfigModel", bound=BaseModel)
ExternalTypeDef = TypeVar("ExternalTypeDef", bound=BaseModel)

class Marshal(ABC, Generic[ConfigModel, ExternalTypeDef]):
    """
    Abstract class for defining a Marshal class. The purpose of marshalling is to transform a given input to the
    required, use-case specific output, based on domain specific knowledge and the configuration by the user.

    Methods defined in the Marshal are supposed to be called from the Jinja template that renders the output.
    """

    class MarshalException(Exception):
        """Marshalling error"""

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

    def marshal(self, type_defs: list[BaseType]):
        """
        Marshals the provided type and all the fields that belong to it.

        Uses the Visitor pattern to visit each relevant element in the AST and searches for a matching method to
        do the marshalling.

        Valid marshalling functions are named by the type definitions full class name prefixed with `marshal_`.
        Type definitions can optionally be marshalled a second time to circumvent cyclic dependencies.
        The second marshalling method is prefixed with `second_`.

        The hierarchy of the given type is tarversed all the way up to its common pydantic superclass `BaseModel`,
        until a matching method can be found.

        Examples:
            - Type `Interface`: `marshal_interface`, `second_interface` in the second run.
            - Field `Interface.Method`: `marshal_interface_method`, `marshal_base_field` if not found.

        Args:
            type_def: Type definition that should be marshalled.


        Raises:
            Marshal.MarshalException: - if marshalling results in an output that would not be valid in the target language
                                        (e.g. because it contains a reserved keyword).
                                      - if no matching marshal method can be found in the first run. This means that
                                        the feature is not implemented for the current language and processing must be
                                        stopped.


        """

        def call_marshal_method(definition: BaseModel, second: bool = False):
            def traverse_hierarchy(def_class, definition):
                if def_class in [BaseExternalType, BaseModel] and not second:
                    raise Marshal.MarshalException(
                        definition,
                        f"Language feature '{definition.__class__.__qualname__}' is not supported for the target '{self.key}'"
                    )
                qualifier = '_'.join([word.lower() for word in re.findall(r'[A-Z][a-z0-9]*', def_class.__qualname__)])
                method_name = f"second_{qualifier}" if second else f"marshal_{qualifier}"
                if hasattr(self, method_name):
                    getattr(self, method_name)(definition)
                else:
                    for base in def_class.__bases__:
                        traverse_hierarchy(base, definition)

            traverse_hierarchy(definition.__class__, definition)

        def marshal_types(type_defs: list[BaseType], second: bool = False):
            for type_def in type_defs:
                try:
                    call_marshal_method(type_def, second)
                except pydantic.ValidationError as e:
                    raise Marshal.MarshalException(type_def, str(e))

        def marshal_fields(type_defs: list[BaseType], second: bool = False):
            for type_def in type_defs:
                try:
                    match type_def:
                        case Function():
                            for parameter in type_def.parameters:
                                call_marshal_method(parameter, second)
                        case Record():
                            for field_def in type_def.fields:
                                call_marshal_method(field_def, second)
                            for constant in type_def.constants:
                                call_marshal_method(constant, second)
                        case Interface():
                            for method in type_def.methods:
                                for parameter in method.parameters:
                                    call_marshal_method(parameter, second)
                                call_marshal_method(method, second)
                            for property_def in type_def.properties:
                                call_marshal_method(property_def, second)
                            for constant in type_def.constants:
                                call_marshal_method(constant, second)
                        case Enum():
                            for item in type_def.items:
                                call_marshal_method(item, second)
                        case Flags():
                            for flag in type_def.flags:
                                call_marshal_method(flag, second)
                except pydantic.ValidationError as e:
                    raise Marshal.MarshalException(type_def, str(e))

        if self.config:
            marshal_types(type_defs)
            marshal_types(type_defs, second=True)
            marshal_fields(type_defs)
            marshal_fields(type_defs, second=True)
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")
