from pathlib import Path

import mistletoe

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseField, BaseType
from .comment_renderer import DocCCommentRenderer
from .external_types import external_types
from .type import ObjcExternalType, ObjcType, ObjcField
from .config import ObjcConfig


class ObjcMarshal(Marshal[ObjcConfig, ObjcExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        prefix = self.config.type_prefix if self.config.type_prefix else ""
        type_def.objc = ObjcType(
            boxed=f"{prefix}{type_def.name.convert(self.config.identifier.type)}",
            comment=mistletoe.markdown(type_def.comment, DocCCommentRenderer) if type_def.comment else '',
            header=Path(f"{prefix}{type_def.name.convert(self.config.identifier.file)}.{self.config.header_extension}")
        )

    def marshal_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, DocCCommentRenderer) if field_def.comment else ''
        prefix = self.config.type_prefix if self.config.type_prefix else ""
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.objc = ObjcField(
                    name=f"{prefix}{field_def.name.convert(self.config.identifier.enum)}",
                    comment=comment
                )
            case Record.Field() | Interface.Method.Parameter():
                field_def.objc = ObjcField(
                    name=field_def.name.convert(self.config.identifier.field),
                    comment=comment
                )
            case Interface.Method():
                field_def.objc = ObjcField(
                    name=field_def.name.convert(self.config.identifier.method),
                    comment=comment
                )
