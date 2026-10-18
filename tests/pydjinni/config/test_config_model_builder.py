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


lazy from collections.abc import Callable

import pytest
from pydantic import ValidationError

from pydjinni.config.configuration_model_builder import BaseConfiguration, ConfigurationModelBuilder
from pydjinni.config.model.base_configuration import BaseTargetConfiguration


class CppTargetConfiguration(BaseTargetConfiguration):
    """foo"""

    foo: int = 1


class OtherTargetConfiguration(BaseTargetConfiguration):
    """A distinct target configuration for type mismatch tests."""


@pytest.fixture
def ConfigurationModel() -> type[BaseConfiguration]:
    builder = ConfigurationModelBuilder()
    builder.add_generator_target_configuration("cpp", CppTargetConfiguration)
    return builder.build()


def test_configuration_builder_model_validate(ConfigurationModel: type[BaseConfiguration]):
    # WHEN deserializing a dict into the model returned by the ConfigurationModelBuilder
    config_instance = ConfigurationModel.model_validate({
        "generate": {
            "targets": {
                "cpp": {"foo": 1},
            },
        }
    })

    # THEN the deserialized dict should contain the target configuration
    assert config_instance.generate
    configuration = config_instance.generate.targets.get_configuration("cpp", CppTargetConfiguration)
    assert configuration
    assert configuration.foo == 1


def test_get_configuration_raises_for_wrong_type(ConfigurationModel: type[BaseConfiguration]):
    config_instance = ConfigurationModel.model_validate({
        "generate": {
            "targets": {
                "cpp": {"foo": 1},
            },
        }
    })

    assert config_instance.generate
    with pytest.raises(TypeError, match=r"CppTargetConfiguration.*OtherTargetConfiguration"):
        config_instance.generate.targets.get_configuration("cpp", OtherTargetConfiguration)


@pytest.mark.parametrize(
    "add_target_configuration",
    [
        ConfigurationModelBuilder.add_generator_target_configuration,
        ConfigurationModelBuilder.add_documentation_target_configuration,
        ConfigurationModelBuilder.add_builder_target_configuration,
        ConfigurationModelBuilder.add_package_target_configuration,
    ],
)
def test_configuration_builder_rejects_duplicate_target_keys(
    add_target_configuration: Callable[
        [ConfigurationModelBuilder, str, type[BaseTargetConfiguration]],
        None,
    ],
):
    # GIVEN a ConfigurationModelBuilder with a registered target configuration for the key 'cpp'
    builder = ConfigurationModelBuilder()
    add_target_configuration(builder, "cpp", CppTargetConfiguration)

    # WHEN adding a configuration for a key that already exists
    # THEN a ValueError is raised.
    with pytest.raises(ValueError, match="already registered"):
        add_target_configuration(builder, "cpp", CppTargetConfiguration)


def test_configuration_builder_model_extra_forbid(ConfigurationModel: type[BaseConfiguration]):
    # WHEN deserializing a dict with extra fields in the "generate" block
    # THEN a ValidationError should be raised
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ConfigurationModel.model_validate({
            "generate": {
                "unknown-foo": "bar",
                "targets": {
                    "cpp": {"foo": 1},
                },
            }
        })


def test_configuration_builder_model_target_extra_ignore(ConfigurationModel: type[BaseConfiguration]):
    # WHEN deserializing a dict with extra fields in the "targets" block
    # THEN no error should be raised, because the extra input is ignored
    ConfigurationModel.model_validate({
        "generate": {
            "targets": {
                "unknown-foo": "bar",
                "cpp": {"foo": 1},
            },
        }
    })
