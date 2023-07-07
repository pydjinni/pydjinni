from pathlib import Path

from pydjinni.generator.marshal import Marshal
from pydjinni.parser.ast import Enum, Flags, Interface, Record, Parameter
from pydjinni.parser.base_models import BaseType, BaseField, TypeReference
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
            if parameter.type_ref.optional:
                parameter_type_signatures += parameter.type_ref.type_def.jni.boxed_type_signature
            else:
                parameter_type_signatures += parameter.type_ref.type_def.jni.type_signature
        return_type_signature = ""
        if method.return_type_ref:
            if method.return_type_ref.optional:
                return_type_signature = method.return_type_ref.type_def.jni.boxed_type_signature
            else:
                return_type_signature = method.return_type_ref.type_def.jni.type_signature
        return f"({parameter_type_signatures}){return_type_signature}"

    def marshal_base_type(self, type_def: BaseType):
        namespace = self.config.namespace + [identifier.convert(self.config.identifier.namespace) for identifier in type_def.namespace]
        name = type_def.name.convert(self.config.identifier.class_name)
        java_path = type_def.java.package.split('.') + [name]
        class_descriptor = '/'.join(java_path)
        type_def.jni = JniType(
            name=name,
            translator="::" + "::".join(namespace + [name]),
            typename=NativeType.object,
            header=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.header_extension}"),
            source=Path(f"{type_def.name.convert(self.config.identifier.file)}.{self.config.source_extension}"),
            namespace="::".join(namespace),
            type_signature=f"L{class_descriptor};",
            boxed_type_signature=f"L{class_descriptor};",
            class_descriptor=class_descriptor,
            jni_prefix=self.marshal_jni_prefix(["Java"] + java_path),
        )

    def _get_field_accessor(self, type_ref: TypeReference) -> str:
        native_type = type_ref.type_def.jni.typename
        type = NativeType.object if native_type in [NativeType.string, NativeType.byte_array] or type_ref.optional else native_type
        return f"Get{type[1:].capitalize()}Field"

    def _get_routine_name(self, type_ref: TypeReference) -> str:
        if type_ref:
            native_type = type_ref.type_def.jni.typename
            if native_type in [NativeType.string, NativeType.byte_array] or type_ref.optional:
                native_type = NativeType.object
        else:
            native_type = "Void"
        return f"Call{native_type[1:].capitalize()}Method"

    def _get_typename(self, type_ref: TypeReference) -> str:
        if type_ref:
            if type_ref.optional and type_ref.type_def.jni.typename not in [NativeType.string, NativeType.byte_array]:
                return NativeType.object.value
            else:
                return type_ref.type_def.jni.typename.value
        else:
            return ""

    def marshal_base_field(self, field_def: BaseField):
        match field_def:
            case Enum.Item() | Flags.Flag():
                field_def.jni = JniField(
                    name=field_def.name.convert(self.config.identifier.enum)
                )
            case Record.Field() | Parameter():
                field_def.jni = JniField(
                    name=field_def.name.convert(self.config.identifier.field),
                    field_accessor=self._get_field_accessor(field_def.type_ref),
                    typename= self._get_typename(field_def.type_ref)
                )
            case Interface.Method():
                name = field_def.name.convert(self.config.identifier.method)
                field_def.jni = JniField(
                    name=name,
                    jni_name=name,
                    type_signature=self._marshal_method_type_signature(field_def),
                    routine_name=self._get_routine_name(field_def.return_type_ref)
                )
