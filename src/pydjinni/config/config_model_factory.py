from __future__ import annotations

from pydantic import create_model, BaseModel


class ConfigModelFactory:
    """
    Generates the final config schema from all loaded plugins
    """

    def __init__(self):
        self._generator_config_models: dict[str, type[BaseModel]] = {}

    def add_generator_config(self, name: str, config_model: type[BaseModel]):
        self._generator_config_models[name] = config_model

    def build(self):
        return create_model(
            "Config",
            generate=(self._create_generate_config_model(), None)
        )

    def _create_generate_config_model(self):
        field_kwargs ={key: (config_model, None) for key, config_model in self._generator_config_models.items()}
        return create_model(
            "Generate",
            **field_kwargs
        )
