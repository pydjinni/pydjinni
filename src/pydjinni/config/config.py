import yaml
from pydjinni.exceptions import ParsingException
from pathlib import Path
from logging import Logger
import pydantic
import dataclasses
from pydantic.dataclasses import dataclass
from collections import defaultdict
from pydjinni.regex_datatypes import CppNamespace, JavaPackage, JavaClass, JavaAnnotation
from enum import Enum
from rich.pretty import pretty_repr

def _parse_option(option: str, option_group: str) -> dict:
    key_list, value = option.split('=', 1)
    keys = key_list.split('.')
    keys.insert(0, option_group)
    result = defaultdict()
    d = result
    for subkey in keys[:-1]:
        d = d.setdefault(subkey, {})
    d[keys[-1]] = value
    return result

def _combine_into(d: dict, combined: dict) -> None:
    for k, v in d.items():
        if isinstance(v, dict):
            _combine_into(v, combined.setdefault(k, {}))
        else:
            combined[k] = v

@dataclass
class OutPaths:
    source: Path = dataclasses.field(
        metadata=dict(
            description="The output directory for source files",
        )
    )
    header: Path = dataclasses.field(
        metadata=dict(
            description="The output directory for header files",
        )
    )



@dataclass
class IdentifierStyle:
    class Case(str, Enum):
        camel = 'camelCase'
        pascal = 'PascalCase'
        snake = 'snake_case'
        kebab = 'kebab-case'
        train = 'TRAIN_CASE'
    style: Case
    prefix: str = None

@dataclass
class Config:
    @staticmethod
    def load(path: Path, options: tuple[str], option_group: str, logger: Logger) -> "Config":
        try:
            logger.debug("Loading configuration")
            config_dict = yaml.safe_load(path.read_text())
            for option in options:
                _combine_into(_parse_option(option, option_group), config_dict)
            logger.debug(pretty_repr(config_dict))
            config = Config.__pydantic_model__.parse_obj(config_dict)
            logger.debug(pretty_repr(config))
            return config
        except pydantic.error_wrappers.ValidationError as e:
            raise ParsingException(e)

    @dataclass
    class Generate:
        @dataclass
        class Java:
            class ClassAccessModifier(str, Enum):
                public = 'public'
                package = 'package'

            out: Path = dataclasses.field(
                default=None,
                metadata=dict(
                    description="The output for the Java files",
                    examples=[
                        "path/to/java/output"
                    ]
                )
            )
            package: JavaPackage | None = dataclasses.field(
                default=None,
                metadata=dict(
                    description="The package name to use for generated Java classes",
                )
            )
            interfaces: bool = dataclasses.field(
                default=False,
                metadata=dict(
                    description="Whether Java interfaces should be used instead of abstract classes where possible"
                )
            )
            class_access_modifier: ClassAccessModifier = dataclasses.field(
                default=ClassAccessModifier.public,
                metadata=dict(
                    description="The access modifier to use for generated Java classes",
                )
            )
            cpp_exception: JavaClass = dataclasses.field(
                default="java.lang.RuntimeException",
                metadata=dict(
                    description="The type for translated C++ exceptions in Java",
                )
            )
            annotation: JavaAnnotation = dataclasses.field(
                default=None,
                metadata=dict(
                    description="Java annotation to place on all generated Java classes",
                    examples=["@Foo"]
                )
            )
            use_final_for_record: bool = dataclasses.field(
                default=True,
                metadata=dict(
                    description="Whether generated Java classes for records should be marked `final`",
                )
            )
            @dataclass
            class JavaIdentifierStyles:
                enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
                field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.camel
                type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal

            identifier: JavaIdentifierStyles = JavaIdentifierStyles()

        @dataclass
        class Jni:
            out: Path | OutPaths = dataclasses.field(
                metadata=dict(
                    description="The folder for the JNI C++ output files",
                )
            )
            namespace: CppNamespace = dataclasses.field(
                default=None,
                metadata=dict(
                    description="The namespace name to use for generated JNI C++ classes",
                )
            )

            @dataclass
            class JNIIdentifierStyles:
                class_name: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
                file: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake

            identifier: JNIIdentifierStyles = JNIIdentifierStyles()

        @dataclass
        class Cpp:
            out: Path | OutPaths = dataclasses.field(
                metadata=dict(
                    description="The output folder for C++ files ",
                )
            )
            namespace: CppNamespace = dataclasses.field(
                default=None,
                metadata=dict(
                    description="The namespace name to use for generated C++ classes"
                )
            )

            @dataclass
            class CppIdentifierStyles:
                enum: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.train
                field: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
                method: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
                type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
                enum_type: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
                type_param: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.pascal
                local: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake
                file: IdentifierStyle | IdentifierStyle.Case = IdentifierStyle.Case.snake

            identifier: CppIdentifierStyles = CppIdentifierStyles()

        @dataclass
        class Objc:
            out: Path | OutPaths = dataclasses.field(
                metadata=dict(
                    description="The output folder for Objective-C files",
                )
            )
            type_prefix: str = dataclasses.field(
                default = None,
                metadata=dict(
                    description="The prefix for Objective-C data types (usually two or three letters)",
                )
            )

        @dataclass
        class ObjCpp:
            out: Path | OutPaths = dataclasses.field(
                metadata=dict(
                    description="The output folder for private Objective-C++ files",
                )
            )
            namespace: CppNamespace = dataclasses.field(
                default=None,
                metadata=dict(
                    description="The namespace name to use for generated Objective-C++ classes"
                )
            )

        jni: Jni = None
        java: Java = None
        cpp: Cpp = None
        objc: Objc = None
        objcpp: ObjCpp = None
    generate: Generate
