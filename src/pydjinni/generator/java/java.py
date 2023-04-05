from pydantic import Field
from pydjinni.generator.generator import NoHeaderBaseConfig, BaseType
from pydjinni.regex_datatypes import CustomRegexType
from enum import Enum

class JavaPackage(CustomRegexType):
    pattern = r"^[a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_]$"
    examples = ["my.package.name", "other.package.name"]
    error_message = "is not a valid Java package identifier"

class JavaClass(CustomRegexType):
    pattern = r"^([a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_][.])?[a-zA-Z][a-zA-Z0-9_]*$"
    error_message = "is not a valid Java class name"

class JavaPrimitive(CustomRegexType):
    pattern = r"^[a-z]*$"
    error_message = "is not a valid Java primitive type name"

class JavaAnnotation(CustomRegexType):
    pattern = r"^@([a-z][a-z0-9_]*(([.][a-z0-9_]+)+[0-9a-z_])?[.])?[a-zA-Z][a-zA-Z0-9_]*$"
    error_message = "is not a valid Java annotation"

class JavaConfig(NoHeaderBaseConfig):
    """
    Java configuration options
    """
    class ClassAccessModifier(str, Enum):
        public = 'public'
        package = 'package'

    package: JavaPackage | None = Field(
        default=None,
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
    cpp_exception: JavaClass = Field(
        default="java.lang.RuntimeException",
        description="The type for translated C++ exceptions in Java",
    )
    annotation: JavaAnnotation = Field(
        default=None,
        description="Java annotation to place on all generated Java classes",
        examples=["@Foo"]
    )
    use_final_for_record: bool = Field(
        default=True,
        description="Whether generated Java classes for records should be marked `final`",
    )

class JavaType(BaseType):
    """Java type information"""
    typename: JavaPrimitive
    boxed: JavaClass
    reference: bool = True
    generic: bool = False

    @classmethod
    def from_name(cls, name: str):
        return cls(
            typename=name.lower(),
            boxed=name.lower()
        )




