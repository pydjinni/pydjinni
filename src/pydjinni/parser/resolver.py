import yaml
from logging import Logger
from pydjinni.parser.ast import TypeReference, Type
from dataclasses import dataclass
from pathlib import Path
import pydantic
from rich.pretty import pretty_repr
from pydjinni.exceptions import ParsingException

class Resolver:

    @dataclass
    class TypeResolvingException(Exception):
        """Exception raised when the required pydjinni type cannot be found"""
        type_reference: TypeReference

    @dataclass
    class DuplicateTypeException(Exception):
        """Exception raised when the given pydjinni type is already defined"""
        datatype: Type

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
                    types_type = Type.__pydantic_model__.parse_obj(type_dict)
                    self.logger.debug(pretty_repr(types_type))
                    self.register(types_type)
        except pydantic.error_wrappers.ValidationError as e:
            raise ParsingException(e)

    def register(self, datatype: Type):
        if datatype.name in self.registry:
            raise Resolver.DuplicateTypeException(datatype=datatype)
        else:
            self.registry[datatype.name] = datatype
            self.logger.debug(f"registering type '{datatype.name}'")

    def register_all(self, datatypes: list[Type]):
        for datatype in datatypes:
            self.register(datatype)

    def resolve(self, type_reference: TypeReference):
        self.logger.debug(f"looking up type '{type_reference.name}'")
        type_reference.type = self.registry.get(type_reference.name)
        if type_reference.type is None:
            raise Resolver.TypeResolvingException(type_reference=type_reference)
