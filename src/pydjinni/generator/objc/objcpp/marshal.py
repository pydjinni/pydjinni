from pathlib import Path

from pydjinni.config.types import IdentifierStyle
from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseField, BaseType
from .config import ObjcppConfig
from .external_types import external_types
from .type import ObjcppExternalType, ObjcppType, ObjcppField


class ObjcppMarshal(Marshal[ObjcppConfig, ObjcppExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        namespace = self.marshal_namespace(type_def, IdentifierStyle.Case.pascal, self.config.namespace)
        name = type_def.name.convert(IdentifierStyle.Case.pascal)
        if isinstance(type_def, Enum) or isinstance(type_def, Flags):
            translator = f"::pydjinni::translators::objc::Enum<{type_def.cpp.typename}, {type_def.objc.typename}>"
        else:
            translator = "::" + "::".join(namespace + [name])
        type_def.objcpp = ObjcppType(
            name=name,
            namespace="::".join(namespace),
            header=Path(f"{name}+Private.{self.config.header_extension}"),
            source=Path(f"{name}+Private.{self.config.source_extension}"),
            translator=translator
        )

    def marshal_field(self, field_def: BaseField):
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.objcpp = ObjcppField(
                    name=field_def.name.convert(IdentifierStyle.Case.pascal)
                )
            case Record.Field() | Interface.Method.Parameter():
                field_def.objcpp = ObjcppField(
                    name=field_def.name.convert(IdentifierStyle.Case.camel)
                )
            case Interface.Method():
                field_def.objcpp = ObjcppField(
                    name=field_def.name.convert(IdentifierStyle.Case.camel),
                )
