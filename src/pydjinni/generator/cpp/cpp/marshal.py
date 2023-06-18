from pathlib import Path

import mistletoe

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Interface, Record, Enum, Flags
from pydjinni.parser.base_models import BaseType, BaseField, Constant
from .comment_renderer import DoxygenCommentRenderer
from .config import CppConfig
from .external_types import external_types
from .type import CppExternalType, CppType, CppField


class CppMarshal(Marshal[CppConfig, CppExternalType], types=external_types):

    def marshal_type(self, type_def: BaseType):
        namespace = self.marshal_namespace(type_def, self.config.identifier.namespace, self.config.namespace)
        name = type_def.name.convert(self.config.identifier.type)
        typename = "::" + "::".join(namespace + [name])
        type_def.cpp = CppType(
            name=name,
            typename=typename,
            comment=mistletoe.markdown(type_def.comment, DoxygenCommentRenderer) if type_def.comment else '',
            header=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.header_extension}"),
            source=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.source_extension}"),
            namespace="::".join(namespace),
            proxy=isinstance(type_def, Interface) and self.key in type_def.targets,
            by_value=type(type_def) not in [Interface, Record]
        )

    def marshal_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, DoxygenCommentRenderer) if field_def.comment else ''
        match field_def:
            case Enum.Item() | Flags.Flag():
                style = self.config.identifier.enum
            case Record.Field() | Interface.Method.Parameter():
                style = self.config.identifier.field
            case Constant():
                style = self.config.identifier.const
            case Interface.Method() | _:
                style = self.config.identifier.method

        field_def.cpp = CppField(
            name=field_def.name.convert(style),
            comment=comment
        )

