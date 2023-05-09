from pathlib import Path

import mistletoe

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Interface, Record, Enum, Flags
from pydjinni.parser.base_models import BaseType, BaseField
from .comment_renderer import DoxygenCommentRenderer
from .config import CppConfig
from .external_types import external_types
from .type import CppExternalType, CppType, CppField


class CppMarshal(Marshal[CppConfig, CppExternalType], types=external_types):

    def includes(self, type_def: BaseType) -> list[Path]:
        includes_list: list[Path] = []
        match type_def:
            case Record():
                includes_list = [type_dep.type_ref.type_def.cpp.header for type_dep in type_def.fields]
            case Interface():
                for method in type_def.methods:
                    includes_list += [param.type_ref.type_def.cpp.header for param in method.parameters]
                    if method.return_type_ref is not None:
                        includes_list.append(method.return_type_ref.type_def.cpp.header)
        return [*set(includes_list)]

    def marshal_type(self, type_def: BaseType):
        type_def.cpp = CppType(
            typename=type_def.name.convert(self.config.identifier.type),
            comment=mistletoe.markdown(type_def.comment, DoxygenCommentRenderer) if type_def.comment else '',
            header=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.header_extension}"),
            source=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.source_extension}"),
            includes=self.includes(type_def),
            proxy=isinstance(type_def, Interface) and self.key in type_def.targets
        )

    def marshal_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, DoxygenCommentRenderer) if field_def.comment else ''
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.cpp = CppField(
                    name=field_def.name.convert(self.config.identifier.enum),
                    comment=comment
                )
            case Record.Field() | Interface.Method.Parameter():
                field_def.cpp = CppField(
                    name=field_def.name.convert(self.config.identifier.field),
                    comment=comment
                )
            case Interface.Method():
                field_def.cpp = CppField(
                    name=field_def.name.convert(self.config.identifier.method),
                    comment=comment
                )


