from pathlib import Path

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Interface, Record
from pydjinni.parser.base_models import BaseType, BaseField
from .config import JniConfig
from .external_types import external_types
from .type import JniField, JniType, JniExternalType, NativeType


class JniMarshal(Marshal[JniConfig, JniExternalType], types=external_types):

    def marshal_jni_prefix(self, segments: list[str]):
        segments = [segment.replace("_", "_1") for segment in segments]
        segments = [segment.replace("$", "_00024") for segment in segments]
        return "_".join(segments)

    def _marshal_method_type_signature(self, method: Interface.Method):
        parameter_type_signatures = ""
        for parameter in method.parameters:
            if parameter.type_ref.type_def.jni.typename is NativeType.object:
                parameter_type_signatures += f"L{parameter.type_ref.type_def.jni.type_signature};"
            else:
                parameter_type_signatures += parameter.type_ref.type_def.jni.type_signature
        return_type_signature = method.return_type_ref.type_def.jni.type_signature if method.return_type_ref else ""
        return f"({parameter_type_signatures}){return_type_signature}"

    def marshal_type(self, type_def: BaseType):
        namespace = self.marshal_namespace(type_def, self.config.identifier.namespace, self.config.namespace)
        name = type_def.name.convert(self.config.identifier.class_name)
        java_path = type_def.java.package.split('.') + [name]
        type_def.jni = JniType(
            name=name,
            translator="::" + "::".join(namespace + [name]),
            typename=NativeType.object,
            header=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.header_extension}"),
            source=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.source_extension}"),
            namespace="::".join(namespace),
            type_signature='/'.join(java_path),
            jni_prefix=self.marshal_jni_prefix(["Java"] + java_path),
        )

    def _get_field_accessor(self, native_type: NativeType) -> str:
        type = NativeType.object if native_type is NativeType.string else native_type
        return f"Get{type[1:].capitalize()}Field"

    def marshal_field(self, field_def: BaseField):
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.jni = JniField(
                    name=field_def.name.convert(self.config.identifier.enum)
                )
            case Record.Field() | Interface.Method.Parameter():
                field_def.jni = JniField(
                    name=field_def.name.convert(self.config.identifier.field),
                    field_accessor=self._get_field_accessor(field_def.type_ref.type_def.jni.typename)
                )
            case Interface.Method():
                name = field_def.name.convert(self.config.identifier.method)
                field_def.jni = JniField(
                    name=name,
                    jni_name=name,
                    type_signature=self._marshal_method_type_signature(field_def),
                    routine_name=f"Call{field_def.return_type_ref.type_def.jni.typename[1:].capitalize() if field_def.return_type_ref else 'Void'}Method"
                )
