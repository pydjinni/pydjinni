from .config import JniConfig
from .external_types import external_types
from .type import JniField, JniType, JniExternalType
from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Interface, Record
from pydjinni.parser.base_models import BaseType, BaseField


class JniMarshal(Marshal[JniConfig, JniExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        type_def.jni = JniType(
            translator=type_def.name.convert(self.config.identifier.class_name),
            typename=type_def.name.convert(self.config.identifier.class_name),
            header=self.header_path() / f"{type_def.name.convert(self.config.identifier.file)}.{self.config.header_extension}",
            source=self.source_path() / f"{type_def.name.convert(self.config.identifier.file)}.{self.config.source_extension}",
            type_signature="(ILjava/lang/String;[I)J",
            namespace=self.config.namespace
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
