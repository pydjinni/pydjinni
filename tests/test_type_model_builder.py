from pydantic import BaseModel

from pydjinni.parser.type_model_builder import TypeModelBuilder


def test_add_field():
    # GIVEN a base type model
    class BaseTypeModel(BaseModel, extra="allow"):
        foo: int = 1

    # AND GIVEN a TypeModelFactory
    builder = TypeModelBuilder(BaseTypeModel)

    # AND GIVEN a Field type model
    class FieldTypeModel(BaseModel):
        bar: int = 2

    # WHEN adding the field
    builder.add_field("name", FieldTypeModel)

    # AND WHEN building the model
    type_model = builder.build()

    # THEN the model should contain the field
    assert "name" in type_model.model_fields
    assert type_model.model_fields["name"].annotation == FieldTypeModel
