from pathlib import Path

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Interface, Record
from pydjinni.parser.base_models import BaseType, BaseField
from .config import JniConfig
from .external_types import external_types
from .type import JniField, JniType, JniExternalType


class JniMarshal(Marshal[JniConfig, JniExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        namespace = self.marshal_namespace(type_def, self.config.identifier.namespace, self.config.namespace)
        name = type_def.name.convert(self.config.identifier.class_name)
        type_def.jni = JniType(
            name=name,
            translator="::".join(namespace + [name]),
            typename='jobject',
            header=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.header_extension}"),
            source=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.source_extension}"),
            namespace="::".join(namespace),
            type_signature="(ILjava/lang/String;[I)J",
        )

    def marshal_field(self, field_def: BaseField):
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.jni = JniField(
                    name=field_def.name.convert(self.config.identifier.enum)
                )
            case Record.Field() | Interface.Method.Parameter():
                field_def.jni = JniField(
                    name=field_def.name.convert(self.config.identifier.field)
                )
            case Interface.Method():
                field_def.jni = JniField(
                    name=field_def.name.convert(self.config.identifier.method)
                )
