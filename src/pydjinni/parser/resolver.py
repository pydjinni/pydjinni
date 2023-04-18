from __future__ import annotations

from typing import Any

import yaml
from logging import Logger

from pydjinni.parser.ast import TypeReference, BaseType
from dataclasses import dataclass
from pathlib import Path
import pydantic
from rich.pretty import pretty_repr
from pydjinni.exceptions import ParsingException
from pydjinni.parser.base_models import BaseExternalType


class Resolver:
    @dataclass
    class TypeResolvingException(Exception):
        """Exception raised when the required pydjinni type cannot be found"""
        type_reference: TypeReference

    @dataclass
    class DuplicateTypeException(Exception):
        """Exception raised when the given pydjinni type is already defined"""
        datatype: BaseType

    def __init__(self, logger: Logger):
        self.logger = logger
        self.registry = dict()

    def load(self, path: Path):
        try:
            self.logger.debug(f"Loading types from {path}:")
            types_dict = yaml.safe_load_all(path.read_text())
            for type_dict in types_dict:
                if type_dict is not None:
                    self.logger.debug(pretty_repr(type_dict))
                    types_type = BaseType.parse_obj(type_dict)
                    self.logger.debug(pretty_repr(types_type))
                    self.register(types_type)
        except pydantic.ValidationError as e:
            raise ParsingException(e)

    def register(self, datatype: BaseType):
        if datatype.name in self.registry:
            raise Resolver.DuplicateTypeException(datatype=datatype)
        else:
            self.registry[datatype.name] = datatype
            self.logger.debug(f"registering type '{datatype.name}':\n{pretty_repr(datatype)}")

    def register_external(self, type_definition: BaseExternalType):
        self.registry[type_definition.name] = type_definition
        self.logger.debug(f"registering external type '{type_definition.name}':\n{pretty_repr(type_definition)}")



    def resolve(self, type_reference: TypeReference):
        self.logger.debug(f"looking up type '{type_reference.name}'")
        type_reference.type_def = self.registry.get(type_reference.name)
        if type_reference.type_def is None:
            raise Resolver.TypeResolvingException(type_reference=type_reference)
