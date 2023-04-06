from pathlib import Path

from .objc import ObjcConfig, ObjcType
from .objcpp import ObjCppConfig, ObjCppType
from pydjinni.generator.generator import Generator, Target, IdentifierDefaultsConfig
from ...config.types import IdentifierStyle

objc_target = Target(
    key="objc",
    generators=[
        Generator(
            key="objc",
            config=ObjcConfig,
            identifier=IdentifierDefaultsConfig(
                file=IdentifierStyle.Case.pascal,
                enum=IdentifierStyle.Case.pascal,
                field=IdentifierStyle.Case.camel,
                method=IdentifierStyle.Case.camel,
                type=IdentifierStyle.Case.pascal,
                param=IdentifierStyle.Case.pascal,
                local=IdentifierStyle.Case.camel
            ),
            reserved_keywords=["void", "float", "id", "const", "self", "super"],
            type_config=ObjcType,
            types={
                'i8': ObjcType(
                    typename="int8_t",
                    boxed="NSNumber",
                    header=Path("<cstdint>"),
                    pointer=False
                ),
                'i16': ObjcType(
                    typename="int16_t",
                    boxed="NSNumber",
                    header=Path("<cstdint>"),
                    pointer=False
                )
            }
        ),
        Generator(
            key="objcpp",
            config=ObjCppConfig,
            identifier=IdentifierDefaultsConfig(
                file=IdentifierStyle.Case.snake
            ), reserved_keywords=[
                "void", "float", "id", "const", "self", "super", "auto", "catch",
                "char", "const", "new", "or", "return", "while"
            ],
            type_config=ObjCppType,
            types={
                'i8': ObjCppType(
                    translator="::pydjinni::translators::objc::I8",
                    header=Path("pydjinni/translators/objc/int.hpp")
                ),
                'i16': ObjCppType(
                    translator="::pydjinni::translators::objc::I16",
                    header=Path("pydjinni/translators/objc/int.hpp")
                )
            }
        )
    ]
)
