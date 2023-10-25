# Copyright 2023 jothepro
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

