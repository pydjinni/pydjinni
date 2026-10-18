# Copyright 2023 - 2026 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import override

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

lazy from pydjinni.builder.build_config import BuildBaseConfig
lazy from pydjinni.generator.docs.config import DocumentationBaseConfig
lazy from pydjinni.generator.generate_config import GenerateBaseConfiguration
lazy from pydjinni.packaging.packaging_config import PackageBaseConfig


class BaseConfiguration(BaseSettings):
    """Global PyDjinni settings base configuration."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        env_file=".env",
        env_nested_delimiter="__",
        env_prefix="pydjinni__",
        arbitrary_types_allowed=False,
    )

    generate: GenerateBaseConfiguration | None = None
    documentation: DocumentationBaseConfig | None = None
    build: BuildBaseConfig | None = None
    package: PackageBaseConfig | None = None

    @override
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return env_settings, dotenv_settings, file_secret_settings, init_settings


class BaseTargetConfiguration(BaseModel):
    """Base class for all target configurations."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class BaseTargetsConfiguration(BaseModel):
    """Configurations for all available targets."""

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
    )

    def get_configuration[T: BaseTargetConfiguration](self, key: str, configuration_type: type[T]) -> T | None:
        """type-safe target configuration getter.

        Returns:
            T: the configuration for the given target key if it exists.
            None: if the key cannot be found or its configuration is unset.

        Raises:
            TypeError: if a configuration exists for the key but has a different type.
        """
        configuration = getattr(self, key, None)
        if configuration is None:
            return None
        if not isinstance(configuration, configuration_type):
            raise TypeError(
                f"Configuration for {key!r} is {type(configuration).__name__}, not {configuration_type.__name__}"
            )
        return configuration


class BaseTaskConfiguration(BaseModel):
    """Base class for all task configuration models (generate, build, package, documentation)."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )
    targets: BaseTargetsConfiguration
