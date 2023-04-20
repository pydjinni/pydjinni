from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Record, Interface, Flags
from pydjinni.parser.base_models import BaseType, BaseField
from .config import JavaConfig
from .external_types import external_types
from .type import JavaType, JavaField, JavaExternalType


class JavaMarshal(Marshal[JavaConfig, JavaExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        type_def.java = JavaType(
            boxed=type_def.name.convert(self.config.identifier.type),
            source=self.config.out / f"{type_def.name.convert(self.config.identifier.file)}.java"
        )

    def marshal_field(self, field_def: BaseField):
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.java = JavaField(
                    name=field_def.name.convert(self.config.identifier.enum)
                )
            case Record.Field() | Interface.Method.Parameter():
                field_def.java = JavaField(
                    name=field_def.name.convert(self.config.identifier.field)
                )
            case Interface.Method():
                field_def.java = JavaField(
                    name=field_def.name.convert(self.config.identifier.method)
                )


