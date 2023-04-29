from pydjinni.file.processed_files_model_builder import ProcessedFilesModelBuilder


def test_add_generated_field():
    # GIVEN a ProcessedFilesModelBuilder instance
    builder = ProcessedFilesModelBuilder()

    # WHEN adding a generated field with both header and source output enabled
    builder.add_generated_field("foo", header=True, source=True)

    # AND when building and instantiating the model
    model = builder.build()
    model_instance = model()

    # THEN the model should have the generated field
    assert "generated" in model_instance.model_fields

    # THEN the generated field should have a field for the 'foo' generator output with both header and source fields
    assert "foo" in model_instance.generated.model_fields
    assert "source" in model_instance.generated.foo.model_fields
    assert "header" in model_instance.generated.foo.model_fields


def test_add_source_only_generated_field():
    # GIVEN a ProcessedFilesModelBuilder instance
    builder = ProcessedFilesModelBuilder()

    # WHEN adding a generated field with both header and source output enabled
    builder.add_generated_field("foo", header=False, source=True)

    # AND when building and instantiating the model
    model = builder.build()
    model_instance = model()

    # THEN the model should have the generated field
    assert "generated" in model_instance.model_fields

    # THEN the generated field should have a field for the 'foo' generator output with both header and source fields
    assert "foo" in model_instance.generated.model_fields
    assert "source" in model_instance.generated.foo.model_fields
    assert "header" not in model_instance.generated.foo.model_fields
