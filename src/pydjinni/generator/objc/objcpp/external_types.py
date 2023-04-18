from pathlib import Path

from .type import ObjcppExternalType
from pydjinni.generator.marshal import ExternalTypes

external_types = ExternalTypes[ObjcppExternalType](
    i8=ObjcppExternalType(
        translator="::pydjinni::translators::objc::I8",
        header=Path("pydjinni/translators/objc/int.hpp")
    ),
    i16=ObjcppExternalType(
        translator="::pydjinni::translators::objc::I16",
        header=Path("pydjinni/translators/objc/int.hpp")
    )
)
