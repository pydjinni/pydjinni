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

import inspect
from typing import Any, Final, TypeForm, cast

from pydantic import BaseModel, Field, create_model

from pydjinni.builder.build_config import BuildBaseConfig
from pydjinni.config.model.base_configuration import (
    BaseConfiguration,
    BaseTargetConfiguration,
    BaseTargetsConfiguration,
)
from pydjinni.generator.docs.config import DocumentationBaseConfig
from pydjinni.generator.generate_config import GenerateBaseConfiguration
from pydjinni.packaging.packaging_config import PackageBaseConfig


class ConfigurationModelBuilder:
    """Builder for the final config schema from all loaded plugins."""

    def __init__(self):
        self._generator_config_models: Final[dict[str, type[BaseTargetConfiguration]]] = {}
        self._builder_config_models: Final[dict[str, type[BaseTargetConfiguration]]] = {}
        self._package_config_models: Final[dict[str, type[BaseTargetConfiguration]]] = {}
        self._documentation_config_models: Final[dict[str, type[BaseTargetConfiguration]]] = {}

    @staticmethod
    def _create_config_model[T: BaseModel](
        model_name: str,
        base: type[T],
        models: dict[str, type[BaseTargetConfiguration]],
    ) -> type[T]:
        field_kwargs: dict[str, Any] = {key: (target_config_model, None) for key, target_config_model in models.items()}
        return create_model(
            model_name,
            __base__=base,
            targets=(
                create_model(
                    model_name + "TargetsConfiguration",
                    __base__=BaseTargetsConfiguration,
                    **field_kwargs,
                ),
                Field(
                    description=f"{inspect.getdoc(BaseTargetsConfiguration)} ({','.join(models.keys())})",
                ),
            ),
        )

    def add_generator_target_configuration(self, key: str, config_model: type[BaseTargetConfiguration]):
        """Add a generator target configuration."""
        self._add_target_configuration(self._generator_config_models, key, config_model)

    def add_documentation_target_configuration(self, key: str, config_model: type[BaseTargetConfiguration]):
        """Add a documentation target configuration."""
        self._add_target_configuration(self._documentation_config_models, key, config_model)

    def add_builder_target_configuration(self, key: str, config_model: type[BaseTargetConfiguration]):
        """Add a builder target configuration."""
        self._add_target_configuration(self._builder_config_models, key, config_model)

    def add_package_target_configuration(self, key: str, config_model: type[BaseTargetConfiguration]):
        """Add a package target configuration."""
        self._add_target_configuration(self._package_config_models, key, config_model)

    @staticmethod
    def _add_target_configuration(
        configurations: dict[str, type[BaseTargetConfiguration]],
        key: str,
        config_model: type[BaseTargetConfiguration],
    ) -> None:
        if key in configurations:
            raise ValueError(f"A target configuration for {key!r} is already registered")
        configurations[key] = config_model

    def build(self) -> type[BaseConfiguration]:
        """Return a ``Configuration`` model with all added target configurations."""
        return create_model(
            "Configuration",
            __base__=BaseConfiguration,
            generate=(
                cast(
                    "TypeForm[Any]",
                    self._create_config_model(
                        model_name="GenerateConfiguration",
                        base=GenerateBaseConfiguration,
                        models=self._generator_config_models,
                    )
                    | None,
                ),
                Field(
                    default=None,
                    description=inspect.getdoc(GenerateBaseConfiguration),
                ),
            ),
            documentation=(
                cast(
                    "TypeForm[Any]",
                    self._create_config_model(
                        model_name="DocumentationConfiguration",
                        base=DocumentationBaseConfig,
                        models=self._documentation_config_models,
                    )
                    | None,
                ),
                Field(
                    default=None,
                    description=inspect.getdoc(DocumentationBaseConfig),
                ),
            ),
            build=(
                cast(
                    "TypeForm[Any]",
                    self._create_config_model(
                        model_name="BuildConfiguration",
                        base=BuildBaseConfig,
                        models=self._builder_config_models,
                    )
                    | None,
                ),
                Field(
                    default=None,
                    description=inspect.getdoc(BuildBaseConfig),
                ),
            ),
            package=(
                cast(
                    "TypeForm[Any]",
                    self._create_config_model(
                        model_name="PackageConfiguration",
                        base=PackageBaseConfig,
                        models=self._package_config_models,
                    )
                    | None,
                ),
                Field(
                    default=None,
                    description=inspect.getdoc(PackageBaseConfig),
                ),
            ),
        )
