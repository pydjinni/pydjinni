from pathlib import Path

import mistletoe

from pydjinni.config.types import IdentifierStyle
from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Record, Interface, Flags, Parameter, Function
from pydjinni.parser.base_models import BaseType, BaseField, Constant, TypeReference
from pydjinni.parser.identifier import IdentifierType as Identifier
from .comment_renderer import JavaDocCommentRenderer
from .config import JavaConfig
from .external_types import external_types
from .type import JavaType, JavaField, JavaExternalType


class JavaMarshal(Marshal[JavaConfig, JavaExternalType], types=external_types):
    def _package(self, type_def: BaseType):
        return self.config.package + [identifier.convert(self.config.identifier.package) for identifier in
                                      type_def.namespace]

    def marshal_base_type(self, type_def: BaseType):
        type_def.java = JavaType.create(
            name=type_def.name.convert(self.config.identifier.type),
            package=self._package(type_def),
            comment=type_def.comment
        )

    def marshal_record(self, type_def: Record):
        name = type_def.name
        if self.key in type_def.targets:
            name += "_base"
        package = self._package(type_def)
        type_def.java = JavaType.create(
            name=name.convert(self.config.identifier.type),
            package=package,
            comment=type_def.comment,
            typename='.'.join(package + [type_def.name.convert(self.config.identifier.type)])
        )

    def marshal_flags(self, type_def: Flags):
        package = self.config.package + [identifier.convert(self.config.identifier.package) for identifier in
                                         type_def.namespace]
        name = type_def.name.convert(self.config.identifier.type)
        type_def.java = JavaType.create(
            name=name,
            package=package,
            comment=type_def.comment,
            typename=f"java.util.EnumSet<{'.'.join(package + [name])}>"
        )

    def marshal_function(self, type_def: Function):
        def generate_type_signature(type_ref: TypeReference, depth: int = 0) -> str:
            output = f"{'_' * depth}{type_ref.name.convert(IdentifierStyle.Case.pascal)}"
            for generic_parameter in type_ref.parameters:
                output += generate_type_signature(generic_parameter, depth + 1)
            return output

        if type_def.name == "<anonymous>":
            signature = ""
            for parameter in type_def.parameters:
                signature += f"${generate_type_signature(parameter.type_ref)}"
            if type_def.return_type_ref:
                signature += f"$${generate_type_signature(type_def.return_type_ref)}"
            marshalled_name = f"{self.config.function_prefix}{signature}"
        else:
            marshalled_name = type_def.name.convert(self.config.identifier.type)

        type_def.java = JavaType.create(marshalled_name, package=self.config.package, comment=type_def.comment)

    def marshal_base_field(self, field_def: BaseField):
        comment = mistletoe.markdown(field_def.comment, JavaDocCommentRenderer) if field_def.comment else ''
        match field_def:
            case Enum.Item() | Flags.Flag():
                style = self.config.identifier.enum
            case Record.Field() | Interface.Property():
                style = self.config.identifier.field
            case Constant():
                style = self.config.identifier.const
            case Parameter():
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
