from .objc import ObjcConfig, ObjcType
from .objcpp import ObjCppConfig, ObjCppType
from pydjinni.generator.generator import Generator, Target, IdentifierDefaultsConfig
from .swift import SwiftConfig, SwiftType
from ...config.types import IdentifierStyle

objc_target = Target(
    key="objc",
    generators=[
        Generator(key="objc", config=ObjcConfig, identifier=IdentifierDefaultsConfig(
            file=IdentifierStyle.Case.pascal,
            enum=IdentifierStyle.Case.pascal,
            field=IdentifierStyle.Case.camel,
            method=IdentifierStyle.Case.camel,
            type=IdentifierStyle.Case.pascal,
            param=IdentifierStyle.Case.pascal,
            local=IdentifierStyle.Case.camel
        ), reserved_keywords=["void", "float", "id", "const", "self", "super"], type_config=ObjcType),
        Generator(key="objcpp", config=ObjCppConfig, identifier=IdentifierDefaultsConfig(
            file=IdentifierStyle.Case.snake
        ), reserved_keywords=[
            "void", "float", "id", "const", "self", "super", "auto", "catch",
            "char", "const", "new", "or", "return", "while"
        ], type_config=ObjCppType),
        Generator(
            key="swift",
            config=SwiftConfig,
            identifier=IdentifierDefaultsConfig(
                method=IdentifierStyle.Case.camel
            ),
            reserved_keywords=[
                "init", "deinit"
            ],
            type_config=SwiftType
        )
    ]
)
