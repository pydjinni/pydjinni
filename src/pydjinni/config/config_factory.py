from __future__ import annotations

from pydantic import create_model, Field

from pydjinni.config.types import IdentifierStyle
from pydjinni.generator.generator import Generator, Target, IdentifierDefaultsConfig


class ConfigFactory:
    """
    Generates the final config schema from all loaded plugins
    """
    
    def __init__(self):
        self._generators: list[Generator] = []

    def add_generator(self, generator: Generator) -> ConfigFactory:
        self._generators.append(generator)
        return self

    def add_target(self, target: Target) -> ConfigFactory:
        for generator in target.generators:
            self.add_generator(generator)
        return self

    def build(self):
        return create_model(
            "Config",
            generate=(self._build_generate_config_model(), None)
        )

    def _build_generate_config_model(self):
        def build_identifier_style_config_model(name: str, style_config: IdentifierDefaultsConfig):
            return create_model(
                name,
                **{
                    key:
                        (
                            IdentifierStyle | IdentifierStyle.Case,
                            Field(default=value) if type(value) is IdentifierStyle or type(value) is IdentifierStyle.Case else
                            Field(default=value[1], alias=value[0])
                        )
                    for key, value in style_config.model_dump().items() if value is not None
                }
        )

        def build_generator_config_model(generator: Generator):
            identifier_style_config_model = build_identifier_style_config_model(
                    name=f"{generator.config.__name__}IdentifierStyle",
                    style_config=generator.identifier
                )
            return create_model(
                generator.config.__name__,
                identifier=(identifier_style_config_model, Field(default=identifier_style_config_model(), json_schema_extra={
                    # TODO remove this once https://github.com/pydantic/pydantic/issues/5367 is fixed
                    "default": { value.alias or key: value.default for key, value in identifier_style_config_model.model_fields.items()}
                })),
                __base__=generator.config,
            )

        return create_model(
            "Generate",
            **{_generator.key: (
                build_generator_config_model(generator=_generator), None)
                for _generator in self._generators
            }
        )
