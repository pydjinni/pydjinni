from pathlib import Path

import mistletoe

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Record, Interface, Flags
from pydjinni.parser.base_models import BaseType, BaseField, Constant, BaseClassType
from pydjinni.parser.identifier import Identifier
from .comment_renderer import JavaDocCommentRenderer
from .config import JavaConfig
from .external_types import external_types
from .type import JavaType, JavaField, JavaExternalType


class JavaMarshal(Marshal[JavaConfig, JavaExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        package = self.marshal_namespace(type_def, self.config.identifier.package, self.config.package, ".")
        name = type_def.name
        if isinstance(type_def, Record) and self.key in type_def.targets:
            name += "_base"
        marshalled_name = Identifier(name).convert(self.config.identifier.type)
        match type_def:
            case Flags():
                typename = f"java.util.EnumSet<{'.'.join(package + [marshalled_name])}>"
            case _:
                typename = ".".join(package + [marshalled_name])
        type_def.java = JavaType(
            typename=typename,
            boxed=typename,
            name=marshalled_name,
            source=Path().joinpath(*package) / f"{marshalled_name}.java",
            package=".".join(package),
            comment=mistletoe.markdown(type_def.comment, JavaDocCommentRenderer) if type_def.comment else '',
        )

    def marshal_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, JavaDocCommentRenderer) if field_def.comment else ''
        match field_def:
            case Enum.Item() | Flags.Flag():
                style = self.config.identifier.enum
            case Record.Field() | Interface.Property():
                style = self.config.identifier.field
            case Constant():
                style = self.config.identifier.const
            case Interface.Method.Parameter():
                style = self.config.identifier.field
            case Interface.Method() | _:
                style = self.config.identifier.method

        field_def.java = JavaField(
            name=field_def.name.convert(style),
            getter=Identifier(f"get_{field_def.name}").convert(self.config.identifier.method)
            if type(field_def) in [Record.Field, Interface.Property]
            else None,
            setter=Identifier(f"set_{field_def.name}").convert(self.config.identifier.field)
            if type(field_def) is Interface.Property
            else None,
            comment=comment
        )
