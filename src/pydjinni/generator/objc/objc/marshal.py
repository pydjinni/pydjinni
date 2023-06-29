from pathlib import Path

import mistletoe

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseField, BaseType, Constant, BaseExternalType, BaseClassType, TypeReference
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
                kwargs['init'] = Identifier(f"init_with_{type_def.fields[0].name}").convert(
                    self.config.identifier.method)
                kwargs['convenience_init'] = Identifier(f"{type_def.name}_with_{type_def.fields[0].name}").convert(
                    self.config.identifier.method)
            else:
                kwargs['init'] = "init"
                kwargs['convenience_init'] = type_def.name.convert(self.config.identifier.method)

        type_def.objc = ObjcType(
            typename=typename,
            boxed=typename,
            comment=mistletoe.markdown(type_def.comment, DocCCommentRenderer) if type_def.comment else '',
            header=Path(f"{typename}.{self.config.header_extension}"),
            source=Path(f"{typename}.{self.config.source_extension}"),
            swift_typename=".".join(namespace + [type_def.name.convert(self.config.identifier.type)]),
            pointer=isinstance(type_def, BaseClassType),
            **kwargs
        )

    def _type_decl(self, type_ref: TypeReference, parameter: bool = False, boxed: bool = False) -> str:
        type_def: BaseExternalType | BaseType = type_ref.type_def
        annotation = ""
        generic_types = ""
        pointer = type_def.objc.pointer
        optional = type_ref.optional
        typename = type_def.objc.boxed if boxed or optional else type_def.objc.typename
        if type_ref.parameters:
            generic_types = "<"
            for parameter_ref in type_ref.parameters:
                if len(generic_types) > 1:
                    generic_types += ", "
                generic_types += self._type_decl(parameter_ref, boxed=True)
            generic_types += ">"
        if isinstance(type_def, Interface) or \
                isinstance(type_def, BaseExternalType) and \
                type_def.primitive == BaseExternalType.Primitive.interface:
            if parameter:
                typename = f"id<{typename}>"
                pointer = False

        return f"{typename}{generic_types}{' *' if pointer or boxed or optional else ''}"

    def _annotation(self, type_ref: TypeReference):
        if type_ref and ((isinstance(type_ref.type_def, Interface) or
                          (isinstance(type_ref.type_def, BaseExternalType) and
                          type_ref.type_def.primitive == BaseExternalType.Primitive.interface)) or
                         type_ref.optional):
            return "nullable"
        elif type_ref and type_ref.type_def.objc.pointer:
            return "nonnull"
        else:
            return ""

    def marshal_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, DocCCommentRenderer) if field_def.comment else ''
        match field_def:
            case Enum.Item() | Flags.Flag():
                style = self.config.identifier.enum
                specifier = None
                annotation = None
                type_decl = None
            case Record.Field() | Constant():
                style = self.config.identifier.field
                specifier = None
                annotation = self._annotation(field_def.type_ref)
                type_decl = self._type_decl(field_def.type_ref)
            case Interface.Method.Parameter():
                style = self.config.identifier.field
                specifier = None
                annotation = self._annotation(field_def.type_ref)
                type_decl = self._type_decl(field_def.type_ref, True)
            case Interface.Method() | _:
                style = self.config.identifier.method
                specifier = "+" if field_def.static else "-"
                annotation = self._annotation(field_def.return_type_ref)
                type_decl = self._type_decl(field_def.return_type_ref) if field_def.return_type_ref else ""
        field_def.objc = ObjcField(
            name=field_def.name.convert(style),
            comment=comment,
            specifier=specifier,
            annotation=annotation,
            type_decl=type_decl
        )
