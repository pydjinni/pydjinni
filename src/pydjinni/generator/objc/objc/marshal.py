from pathlib import Path

import mistletoe

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseField, BaseType
from pydjinni.parser.identifier import Identifier
from .comment_renderer import DocCCommentRenderer
from .external_types import external_types
from .type import ObjcExternalType, ObjcType, ObjcField
from .config import ObjcConfig


class ObjcMarshal(Marshal[ObjcConfig, ObjcExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        namespace = self.marshal_namespace(type_def, self.config.identifier.type)
        prefix = self.config.type_prefix if self.config.type_prefix else ""
        typename = f"{prefix}{''.join(namespace)}{type_def.name.convert(self.config.identifier.type)}"
        kwargs = dict()
        if isinstance(type_def, Record):
            if type_def.fields:
                kwargs['init'] = Identifier(f"init_with_{type_def.fields[0].name}").convert(self.config.identifier.method)
                kwargs['convenience_init'] = Identifier(f"{type_def.name}_with_{type_def.fields[0].name}").convert(self.config.identifier.method)
            else:
                kwargs['init'] = "init"
                kwargs['convenience_init'] = type_def.name.convert(self.config.identifier.method)

        type_def.objc = ObjcType(
            typename=typename,
            boxed=typename,
            comment=mistletoe.markdown(type_def.comment, DocCCommentRenderer) if type_def.comment else '',
            header=Path(f"{typename}.{self.config.header_extension}"),
            swift_typename=".".join(namespace + [type_def.name.convert(self.config.identifier.type)]),
            imports=self.includes(type_def),
            **kwargs
        )

    def marshal_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, DocCCommentRenderer) if field_def.comment else ''
        prefix = self.config.type_prefix if self.config.type_prefix else ""
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.objc = ObjcField(
                    name=field_def.name.convert(self.config.identifier.enum),
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
