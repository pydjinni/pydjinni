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

import yaml

from pydjinni.exceptions import ConfigurationException
from pydjinni.generator.generator import Generator
from pydjinni.parser.base_models import BaseType, BaseExternalType
from .config import YamlConfig


class YamlGenerator(Generator):
    key = "yaml"
    config_model = YamlConfig
    writes_source = True

    def generate_type_dict(self, type_def: BaseType) -> dict:
        return type_def.model_dump(mode='json', exclude_none=True, exclude=set(
            [field for field in type_def.model_fields.keys() if field not in (BaseExternalType.model_fields.keys())]))

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        filtered_type_defs = [type_def for type_def in ast if
                              not (type_def.primitive == BaseExternalType.Primitive.function and type_def.anonymous)]
        if self.config:
            if self.config.out_file:
                self._file_writer.write_source(
                    key=self.key,
                    filename=self.source_path / self.config.out_file,
                    content=yaml.dump_all([self.generate_type_dict(type_def) for type_def in filtered_type_defs])
                )
            else:
                for type_def in filtered_type_defs:
                    self._file_writer.write_source(
                        key=self.key,
                        filename=self.source_path / f"{type_def.name}.yaml",
                        content=yaml.dump(self.generate_type_dict(type_def))
                    )
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")
