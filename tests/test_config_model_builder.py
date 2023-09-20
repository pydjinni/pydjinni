from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder


def test_add_generator_config():
    # GIVEN a ConfigModelFactory
    builder = ConfigModelBuilder()

    # AND GIVEN a pydantic model
    class GeneratorConfig(BaseModel):
        """foo"""
        foo: int = 1

    # WHEN adding a generator model
    builder.add_generator_config("name", GeneratorConfig)

    # AND WHEN building the config model
    config_model = builder.build()

    # THEN the config model should contain a 'generate' field
    assert 'generate' in config_model.model_fields

    # THEN the config model should contain the GeneratorConfig model in the generate field
    assert 'name' in config_model.model_fields['generate'].annotation.__args__[0].model_fields
    assert config_model.model_fields['generate'].annotation.__args__[0].model_fields['name'].annotation == GeneratorConfig

