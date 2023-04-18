from pathlib import Path

from .type import JniExternalType
from pydjinni.generator.marshal import ExternalTypes

external_types = ExternalTypes[JniExternalType](
    i8=JniExternalType(
        translator="::pydjinni::translators::jni::I8",
        header=Path("pydjinni/translators/jni/int.hpp"),
        typename='jobject',
        type_signature="B"
    ),
    i16=JniExternalType(
        translator="::pydjinni::translators::jni::I16",
        header=Path("pydjinni/translators/jni/int.hpp"),
        typename='jobject',
        type_signature="S"
    )
)
