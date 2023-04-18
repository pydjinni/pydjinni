from pathlib import Path

from .type import CppExternalType
from pydjinni.generator.marshal import ExternalTypes

external_types = ExternalTypes[CppExternalType](
    i8=CppExternalType(
        typename="int8_t",
        header=Path("<cstdint>")
    ),
    i16=CppExternalType(
        typename="int16_t",
        header=Path("<cstdint>")
    )
)
