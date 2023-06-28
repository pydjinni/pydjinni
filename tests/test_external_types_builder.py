from pydantic import BaseModel

from pydjinni.generator.external_types import ExternalTypesBuilder


def test_register_external_types():
    # GIVEN a specific ExternalType model
    class MyExternalType(BaseModel):
        typename: str

    # AND GIVEN an ExternalBaseType model
    class ExternalBaseType(BaseModel):
        name: str
        my: MyExternalType = None

    # AND GIVEN an ExternalTypesBuilder
    builder = ExternalTypesBuilder(external_base_type=ExternalBaseType)

    # AND GIVEN MyExternalType definitions
    external_types: dict[str, MyExternalType] = {
        "i8": MyExternalType(typename="foo"),
        "i16": MyExternalType(typename="bar")
    }

    # WHEN registering an external type
    builder.register(key="my", external_types=external_types)

    # AND WHEN building the external types
    types = builder.build()

    # THEN the types that are given as MyExternalType definitions should by available for the `my` language
    for external_type in types:
        if external_type.my:
            assert external_type.my == external_types[external_type.name]

