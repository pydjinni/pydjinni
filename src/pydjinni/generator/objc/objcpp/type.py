from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from pydjinni.config.types import IdentifierStyle
from pydjinni.generator.objc.objcpp.config import ObjcppConfig
from pydjinni.parser.base_models import BaseType, BaseField


class ObjcppExternalType(BaseModel):
    translator: str
    header: Path


class ObjcppBaseType(BaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: ObjcppConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self): return self.decl.name.convert(IdentifierStyle.Case.pascal)

    @computed_field
    @cached_property
    def translator(self) -> str: return f"::{self.namespace}::{self.name}"

    @computed_field
    @cached_property
    def header(self) -> Path: return Path(f"{self.name}+Private.{self.config.header_extension}")

    @cached_property
    def source(self) -> Path: return Path(f"{self.name}+Private.{self.config.source_extension}")

    @cached_property
    def namespace(self): return '::'.join(self.config.namespace + [identifier.convert(IdentifierStyle.Case.pascal)
                                                                   for identifier in self.decl.namespace])


class ObjcppBaseField(BaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: ObjcppConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(IdentifierStyle.Case.camel)


class ObjcppSymbolicConstantField(ObjcppBaseField):
    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(IdentifierStyle.Case.pascal)
