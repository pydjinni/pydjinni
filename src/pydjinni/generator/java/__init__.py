from pathlib import Path

from .java import JavaConfig, JavaType
from .jni import JniConfig, JniType
from pydjinni.generator.generator import Generator, Target, IdentifierDefaultsConfig
from ...config.types import IdentifierStyle

java_target = Target(
    key="java",
    generators=[
        Generator(
            key="java",
            config=JavaConfig,
            identifier=IdentifierDefaultsConfig(
                file=IdentifierStyle.Case.pascal,
                enum=IdentifierStyle.Case.train,
                field=IdentifierStyle.Case.camel,
                type=IdentifierStyle.Case.pascal
            ),
            reserved_keywords=["abstract", "assert", "break", "case", "catch", "class", "final", "float", "if", "int"],
            type_config=JavaType,
            types={
                'i8': JavaType(
                    typename='byte',
                    boxed='Byte',
                    reference=False,
                    generic=False
                ),
                'i16': JavaType(
                    typename="short",
                    boxed="Short",
                    reference=False,
                    generic=False
                )
            }
        ),
        Generator(
            key="jni",
            config=JniConfig,
            identifier=IdentifierDefaultsConfig(
                file=IdentifierStyle.Case.snake,
                type=("class_name", IdentifierStyle.Case.pascal)
            ),
            reserved_keywords=["auto", "break", "const", "double", "else", "int", "long"],
            type_config=JniType,
            types={
                'i8': JniType(
                    translator="::pydjinni::translators::jni::I8",
                    header=Path("pydjinni/translators/jni/int.hpp"),
                    typename='jobject',
                    type_signature="B"
                ),
                'i16': JniType(
                    translator="::pydjinni::translators::jni::I16",
                    header=Path("pydjinni/translators/jni/int.hpp"),
                    typename='jobject',
                    type_signature="S"
                )
            }
        )
    ]
)
