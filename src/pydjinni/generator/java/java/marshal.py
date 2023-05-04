import mistletoe

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Record, Interface, Flags
from pydjinni.parser.base_models import BaseType, BaseField
from pydjinni.parser.identifier import Identifier
from .comment_renderer import JavaDocCommentRenderer
from .config import JavaConfig
from .external_types import external_types
from .type import JavaType, JavaField, JavaExternalType


class JavaMarshal(Marshal[JavaConfig, JavaExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        type_def.java = JavaType(
            boxed=type_def.name.convert(self.config.identifier.type),
            source=self.config.out / f"{type_def.name.convert(self.config.identifier.file)}.java",
            comment=mistletoe.markdown(type_def.comment, JavaDocCommentRenderer) if type_def.comment else ''
        )

    def marshal_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, JavaDocCommentRenderer) if field_def.comment else ''
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.java = JavaField(
                    name=field_def.name.convert(self.config.identifier.enum),
                    comment=comment
                )
            case Record.Field():
                field_def.java = JavaField(
                    name=field_def.name.convert(self.config.identifier.field),
                    getter=Identifier(f"get_{field_def.name}").convert(self.config.identifier.method),
                    comment=comment
                )
            case Interface.Method.Parameter():
                field_def.java = JavaField(
                    name=field_def.name.convert(self.config.identifier.field),
                    comment=comment
                )
            case Interface.Method():
                field_def.java = JavaField(
                    name=field_def.name.convert(self.config.identifier.method),
                    comment=comment
                )


