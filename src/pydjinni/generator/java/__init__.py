from .java import JavaConfig, JavaType
from .jni import JniConfig, JniType
from pydjinni.generator.generator import Generator, Target, IdentifierDefaultsConfig
from ...config.types import IdentifierStyle

java_target = Target(
    key="java",
    generators=[
        Generator(key="java", config=JavaConfig, identifier=IdentifierDefaultsConfig(
            file=IdentifierStyle.Case.pascal,
            enum=IdentifierStyle.Case.train,
            field=IdentifierStyle.Case.camel,
            type=IdentifierStyle.Case.pascal,

        ), reserved_keywords=["abstract", "assert", "break", "case", "catch", "class", "final", "float", "if", "int"],
                  type_config=JavaType),
        Generator(key="jni", config=JniConfig, identifier=IdentifierDefaultsConfig(
            file=IdentifierStyle.Case.snake,
            type=("class_name", IdentifierStyle.Case.pascal)
        ), reserved_keywords=["auto", "break", "const", "double", "else", "int", "long"], type_config=JniType)
    ]
)
