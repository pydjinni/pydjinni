from abc import abstractmethod, ABC
from pathlib import Path

from pydantic import BaseModel, Field

from pydjinni.config.types import OutPaths, IdentifierStyle


class BaseConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated files. Separate folders for `source` and `header` files can be specified."
    )

class NoHeaderBaseConfig(BaseModel):
    out: Path = Field(
        default=None,
        description="The output for the generated source files."
    )

class HeaderOnlyBaseConfig(BaseModel):
    out: Path | OutPaths = Field(
        description="The output folder for the generated header files."
    )

class BaseType(BaseModel):
    @classmethod
    @abstractmethod
    def from_name(cls, name: str):
        ...


class Generator:
    def __init__(self, key: str, config, identifier, reserved_keywords: list[str], type_config, types = None):
        self.key = key
        self.config = config
        self.identifier = identifier
        self.reserved_keywords = reserved_keywords
        self.type_config = type_config
        self.types = types

    def generate(self):
        ...

class Target:
    def __init__(self, key: str, generators: list[Generator]):
        self.key = key
        self.generators = generators

    def generate(self):
        res = [generator.generate() for generator in self.generators]


class IdentifierDefaultsConfig(BaseModel):
    file: IdentifierStyle | IdentifierStyle.Case | tuple[str, IdentifierStyle | IdentifierStyle.Case] = None
    enum: IdentifierStyle | IdentifierStyle.Case | tuple[str, IdentifierStyle | IdentifierStyle.Case] = None
    field: IdentifierStyle | IdentifierStyle.Case | tuple[str, IdentifierStyle | IdentifierStyle.Case] = None
    method: IdentifierStyle | IdentifierStyle.Case | tuple[str, IdentifierStyle | IdentifierStyle.Case] = None
    type: IdentifierStyle | IdentifierStyle.Case | tuple[str, IdentifierStyle | IdentifierStyle.Case] = None
    param: IdentifierStyle | IdentifierStyle.Case | tuple[str, IdentifierStyle | IdentifierStyle.Case] = None
    local: IdentifierStyle | IdentifierStyle.Case | tuple[str, IdentifierStyle | IdentifierStyle.Case] = None
