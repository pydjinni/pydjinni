from functools import cached_property
from pathlib import Path

import mistletoe
from pydantic import BaseModel, Field, computed_field

from pydjinni.generator.java.java.comment_renderer import JavaDocCommentRenderer
from pydjinni.generator.java.java.config import JavaConfig
from pydjinni.parser.ast import Record, Function
from pydjinni.parser.base_models import BaseType, BaseField
from pydjinni.parser.identifier import IdentifierType as Identifier


class JavaExternalType(BaseModel):
    """Java type information"""
    typename: str = None
    boxed: str = ""
    reference: bool = True
    generic: bool = False


class JavaBaseType(BaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: JavaConfig = Field(exclude=True, repr=False)

    @cached_property
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.type)

    @computed_field
    @cached_property
    def typename(self) -> str: return f"{self.package}.{self.name}"

    @computed_field
    @cached_property
    def boxed(self) -> str: return self.typename

    @computed_field
    @cached_property
    def reference(self) -> bool: return True

    @computed_field
    @cached_property
    def generic(self) -> bool: return False

    @cached_property
    def package(self) -> str:
        return '.'.join(self.config.package + [identifier.convert(self.config.identifier.package) for identifier in self.decl.namespace])

    @cached_property
    def source(self): return Path(*self.package.split('.')) / f"{self.name}.java"

    @cached_property
    def comment(self): return mistletoe.markdown(self.decl.comment, JavaDocCommentRenderer) if self.decl.comment else ''

    @cached_property
    def class_modifier(self):
        output = ""
        if self.config.class_access_modifier == JavaConfig.ClassAccessModifier.public:
            output += "public "
        return output


class JavaBaseField(BaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: JavaConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.field)

    @cached_property
    def comment(self): return mistletoe.markdown(self.decl.comment, JavaDocCommentRenderer) if self.decl.comment else ''


class JavaRecord(JavaBaseType):
    decl: Record = Field(exclude=True, repr=False)

    @cached_property
    def base_type(self) -> bool:
        return "java" in self.decl.targets

    @cached_property
    def name(self):
        name = self.decl.name
        if self.base_type:
            name += "_base"
        return Identifier(name).convert(self.config.identifier.type)

    @computed_field
    @cached_property
    def typename(self) -> str:
        name = self.decl.name.convert(self.config.identifier.type)
        return f"{self.package}.{name}"

    @cached_property
    def class_modifier(self):
        output = super().class_modifier
        if self.config.use_final_for_record and not self.base_type:
            output += "final "
        return output

    class JavaField(JavaBaseField):
        @cached_property
        def getter(self): return Identifier(f"get_{self.decl.name}").convert(self.config.identifier.method)

        @cached_property
        def field_modifier(self):
            output = ""
            if self.config.use_final_for_record:
                output += "final "
            return output


class JavaFlags(JavaBaseType):
    @computed_field
    @cached_property
    def typename(self) -> str: return f"java.util.EnumSet<{self.package}.{self.name}>"


class JavaFunction(JavaBaseType):
    decl: Function = Field(exclude=True, repr=False)

    @cached_property
    def name(self) -> str:
        if self.decl.anonymous:
            return self.decl.name.title()
        else:
            return super().name


class JavaSymbolicConstantField(JavaBaseField):
    @computed_field
    @cached_property
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.enum)


class JavaInterface(JavaBaseType):

    class JavaMethod(JavaBaseField):
        @computed_field
        @cached_property
        def name(self) -> str: return self.decl.name.convert(self.config.identifier.method)

    class JavaProperty(JavaBaseField):

        @cached_property
        def getter(self): return Identifier(f"get_{self.decl.name}").convert(self.config.identifier.method)
