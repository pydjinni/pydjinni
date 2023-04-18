from .type import JavaExternalType
from pydjinni.generator.marshal import ExternalTypes

external_types = ExternalTypes[JavaExternalType](
    i8=JavaExternalType(
        typename='byte',
        boxed='Byte',
        reference=False,
        generic=False
    ),
    i16=JavaExternalType(
        typename="short",
        boxed="Short",
        reference=False,
        generic=False
    )
)
