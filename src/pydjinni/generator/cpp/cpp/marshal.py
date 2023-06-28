from pathlib import Path

import mistletoe

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Interface, Record, Enum, Flags
from pydjinni.parser.base_models import BaseType, BaseField, Constant, BaseExternalType
from .comment_renderer import DoxygenCommentRenderer
from .config import CppConfig
from .external_types import external_types
from .type import CppExternalType, CppType, CppField


class CppMarshal(Marshal[CppConfig, CppExternalType], types=external_types):

    def _return_type(self, method: Interface.Method):
        output = method.return_type_ref.type_def.cpp.typename if method.return_type_ref else "void"
        if method.return_type_ref and self._check_is_shared_ptr(method.return_type_ref.type_def):
            output = f"std::shared_ptr<{output}>"
        return output

    def _parameter_name(self, type_def: BaseType):
        match type_def:
            case type_def if self._check_is_shared_ptr(type_def):
                return f"const std::shared_ptr<{type_def.cpp.typename}> &"
            case type_def if self._check_is_by_value(type_def):
                return type_def.cpp.typename
            case _:
                return f"const {type_def.cpp.typename} &"

    def _check_is_shared_ptr(self, type_def: BaseType) -> bool:
        return (isinstance(type_def, BaseExternalType) and type_def.primitive == BaseExternalType.Primitive.interface) or \
            type(type_def) is Interface

    def _check_is_by_value(self, type_def: BaseType) -> bool:
        if isinstance(type_def, BaseExternalType):
            return type_def.cpp.by_value
        else:
            return type(type_def) not in [Interface, Record]

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
            by_value=self._check_is_by_value(type_def)
        )


    def marshal_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, DoxygenCommentRenderer) if field_def.comment else ''
        match field_def:
            case Enum.Item() | Flags.Flag():
                style = self.config.identifier.enum
                type_spec = None
            case Record.Field() | Interface.Method.Parameter():
                style = self.config.identifier.field
                type_spec = self._parameter_name(field_def.type_ref.type_def)
            case Constant():
                style = self.config.identifier.const
                type_spec = None
            case Interface.Method() | _:
                style = self.config.identifier.method
                type_spec = self._return_type(field_def)

        field_def.cpp = CppField(
            name=field_def.name.convert(style),
            comment=comment,
            type_spec=type_spec
        )

