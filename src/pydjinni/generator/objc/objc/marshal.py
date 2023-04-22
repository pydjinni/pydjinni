from pathlib import Path

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.base_models import BaseField, BaseType
from .external_types import external_types
from .type import ObjcExternalType, ObjcType
from .config import ObjcConfig


class ObjcMarshal(Marshal[ObjcConfig, ObjcExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        prefix = self.config.type_prefix if self.config.type_prefix else ""
        type_def.objc = ObjcType(
            boxed=f"{prefix}{type_def.name.convert(self.config.identifier.type)}",
            header=Path(f"{prefix}{type_def.name.convert(self.config.identifier.file)}.{self.config.header_extension}")
        )

    def marshal_field(self, field_def: BaseField):
        pass
