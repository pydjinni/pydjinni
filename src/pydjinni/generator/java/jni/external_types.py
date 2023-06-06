from pathlib import Path

from .type import JniExternalType, NativeType
from pydjinni.generator.marshal import ExternalTypes

external_types = ExternalTypes[JniExternalType](
    i8=JniExternalType(
        translator="::pydjinni::jni::translator::I8",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.byte,
        type_signature="B"
    ),
    i16=JniExternalType(
        translator="::pydjinni::translators::jni::I16",
        header=Path("pydjinni/translators/jni/int.hpp"),
        typename=NativeType.short,
        type_signature="S"
    )
)
