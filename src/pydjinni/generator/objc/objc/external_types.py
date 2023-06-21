from pathlib import Path

from .type import ObjcExternalType
from pydjinni.generator.marshal import ExternalTypes

external_types = ExternalTypes[ObjcExternalType](
    i8=ObjcExternalType(
        typename="int8_t",
        boxed="NSNumber",
        header=Path("<Foundation/Foundation.h>"),
        pointer=False
    ),
    i16=ObjcExternalType(
        typename="int16_t",
        boxed="NSNumber",
        header=Path("<Foundation/Foundation.h>"),
        pointer=False
    )
)
