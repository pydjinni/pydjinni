from pydantic import BaseModel

from pydjinni.generator.external_types import ExternalTypesBuilder, ExternalTypes


def test_register_external_types():
    # GIVEN a specific ExternalType model
    class MyExternalType(BaseModel):
        typename: str

    # AND GIVEN an ExternalBaseType model
    class ExternalBaseType(BaseModel):
        name: str
        my: MyExternalType

    # AND GIVEN an ExternalTypesBuilder
    builder = ExternalTypesBuilder(external_base_type=ExternalBaseType)

    # AND GIVEN an ExternalTypes instance
    external_types = ExternalTypes[MyExternalType](
        i8=MyExternalType(typename="foo"),
        i16=MyExternalType(typename="bar")
    )

    # WHEN registering an external type
    builder.register(key="my", external_types=external_types)

    # AND WHEN building the external types
    types = builder.build()

    # THEN types should be a list with all the defined types
    assert len(types) == len(ExternalTypes.model_fields)

    # THEN the name of each type should be equivalent to its ExternalTypes attribute name
    assert types[0].name == list(ExternalTypes.model_fields.keys())[0]

    # THEN each type should contain a key 'my' with a MyExternalType object
    assert types[0].my.typename == "foo"

