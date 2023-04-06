from pydantic import Field
from pydjinni.generator.generator import NoHeaderBaseConfig, BaseType
from enum import Enum

java_class_regex = r"^([a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_][.])?[a-zA-Z][a-zA-Z0-9_]*$"

class JavaConfig(NoHeaderBaseConfig):
    """
    Java configuration options
    """
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
        pattern=java_class_regex,
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

class JavaType(BaseType):
    """Java type information"""
    typename: str = Field(
        pattern=r"^[a-z]*$"
    )
    boxed: str = Field(
        pattern=java_class_regex
    )
    reference: bool = True
    generic: bool = False

    @classmethod
    def from_name(cls, name: str):
        return cls(
            typename=name.lower(),
            boxed=name.lower()
        )




