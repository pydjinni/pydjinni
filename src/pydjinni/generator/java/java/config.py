from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from pydjinni.config.types import IdentifierStyle


class JavaIdentifierStyle(BaseModel):
    enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
    field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
    method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
    package: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
    const: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train


class JavaConfig(BaseModel):
    """
    Java configuration options
    """

    out: Path = Field(
        description="The output folder for the generated files."
    )

    class ClassAccessModifier(str, Enum):
        public = 'public'
        package = 'package'

    package: str = Field(
        default=None,
        pattern=r"^[a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_]$",
        examples=["my.package.name", "other.package.name"],
        description="The package name to use for generated Java classes"
    )
    interfaces: bool = Field(
        default=False,
        description="Whether Java interfaces should be used instead of abstract classes where possible"
    )
    class_access_modifier: ClassAccessModifier = Field(
        default=ClassAccessModifier.public,
        description="The access modifier to use for generated Java classes",
    )
    cpp_exception: str = Field(
        default="java.lang.RuntimeException",
        pattern=r"^([a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_][.])?[a-zA-Z][a-zA-Z0-9_]*$",
        description="The type for translated C++ exceptions in Java",
    )
    annotation: str = Field(
        default=None,
        pattern=r"^@([a-z][a-z0-9_]*(([.][a-z0-9_]+)+[0-9a-z_])?[.])?[a-zA-Z][a-zA-Z0-9_]*$",
        description="Java annotation to place on all generated Java classes",
        examples=["@Foo"]
    )
    use_final_for_record: bool = Field(
        default=True,
        description="Whether generated Java classes for records should be marked `final`",
    )
    native_lib: str = Field(
        default=None,
        description="Name of the native library containing the JNI interface. "
                    "If this option is set and an interface is marked as `main`, a static block will be "
                    "added to the interface, that loads the native library."
    )
    identifier: JavaIdentifierStyle = JavaIdentifierStyle()
