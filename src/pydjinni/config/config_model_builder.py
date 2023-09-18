from __future__ import annotations

from pydantic import create_model, BaseModel
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from pydjinni.builder.build_config import BuildBaseConfig
from pydjinni.generator.generate_config import GenerateBaseConfig
from pydjinni.packaging.packaging_config import PackageBaseConfig

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
                extra='forbid',
                env_file='.env',
                env_nested_delimiter='__',
            )

class ConfigModelBuilder:
    """
    Generates the final config schema from all loaded plugins
    """

    def __init__(self):
        self._generator_config_models: dict[str, type[BaseModel]] = {}
        self._builder_config_models: dict[str, type[BaseModel]] = {}
        self._package_config_models: dict[str, type[BaseModel]] = {}

    def add_generator_config(self, name: str, config_model: type[BaseModel]):
        self._generator_config_models[name] = config_model

    def add_builder_config(self, name: str, config_model: type[BaseModel]):
        self._builder_config_models[name] = config_model

    def add_package_config(self, name: str, config_model: type[BaseModel]):
        self._package_config_models[name] = config_model

    def build(self):
        return create_model(
            "Config",
            __base__=Settings,
            generate=(self._create_config_model("Generate", GenerateBaseConfig, self._generator_config_models),
                      FieldInfo(default=None, description=GenerateBaseConfig.__doc__)),
            build=(self._create_config_model("Build", BuildBaseConfig, self._builder_config_models),
                   FieldInfo(default=None, description=BuildBaseConfig.__doc__)),
            package=(self._create_config_model("Package", PackageBaseConfig, self._package_config_models),
                     FieldInfo(default=None, description=PackageBaseConfig.__doc__)),
        )

    def _create_config_model(self, model_name: str, base: type[BaseModel], models: dict[str, type[BaseModel]]):
        field_kwargs ={key: (config_model, None) for key, config_model in models.items()}
        return create_model(
            model_name,
            __base__=base,
            **field_kwargs
        )
