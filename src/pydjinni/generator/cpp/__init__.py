from pathlib import Path

from .cpp import CppConfig, CppType
from pydjinni.generator.generator import Generator, Target, IdentifierDefaultsConfig
from ...config.types import IdentifierStyle

cpp_target = Target(
    key="cpp",
    generators=[
        Generator(
            key="cpp",
            config=CppConfig,
            identifier=IdentifierDefaultsConfig(
                file=IdentifierStyle.Case.pascal,
                enum=IdentifierStyle.Case.train,
                field=IdentifierStyle.Case.snake,
                method=IdentifierStyle.Case.snake,
                type=IdentifierStyle.Case.pascal,
                param=IdentifierStyle.Case.pascal,
                local=IdentifierStyle.Case.snake
            ),
            reserved_keywords=["auto", "catch", "char", "const", "new", "or", "return", "while"],
            type_config=CppType,
            types={
                'i8': CppType(
                    typename="int8_t",
                    header=Path("<cstdint>")
                ),
                'i16': CppType(
                    typename="int16_t",
                    header=Path("<cstdint>")
                )
            }
        )
    ]
)
