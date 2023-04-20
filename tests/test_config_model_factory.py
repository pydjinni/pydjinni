from pydantic import BaseModel

from pydjinni.config.config_model_factory import ConfigModelFactory


def test_add_generator_config():
    # GIVEN a ConfigModelFactory
    factory = ConfigModelFactory()

    # AND GIVEN a pydantic model
    class GeneratorConfig(BaseModel):
        foo: int = 1

    # WHEN adding a generator model
    factory.add_generator_config("name", GeneratorConfig)

    # AND WHEN building the config model
    config_model = factory.build()

    # THEN the config model should contain a 'generate' field
    assert 'generate' in config_model.model_fields

    # THEN the config model should contain the GeneratorConfig model in the generate field
    assert 'name' in config_model.model_fields['generate'].annotation.model_fields
    assert config_model.model_fields['generate'].annotation.model_fields['name'].annotation == GeneratorConfig

