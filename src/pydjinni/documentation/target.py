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

import inspect
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.documentation.generator import DocumentationGenerator
from pydjinni.parser.base_models import BaseType

DocumentationConfigModel = TypeVar("DocumentationConfigModel", bound=BaseModel)


class DocumentationTarget(ABC):
    @property
    @abstractmethod
    def key(self) -> str:
        pass

    @property
    @abstractmethod
    def config_model(self) -> type[DocumentationConfigModel]:
        """
        The Pydantic model that defines the configuration options for the documentation generator.

        The model will automatically be registered in the system and is then available in the documentation and as part
        of the  JSON-Schema for the configuration file.
        """
        pass

    def __init__(self, config_model_builder: ConfigModelBuilder):
        self.config: DocumentationConfigModel | None = None
        config_model_builder.add_documentation_config(self.key, self.config_model)
        self.generators: list[DocumentationGenerator] = []

        self._generator_directory = Path(inspect.getfile(self.__class__)).parent

        self._jinja_env = Environment(
            loader=FileSystemLoader(self._generator_directory / "templates"),
            trim_blocks=True, lstrip_blocks=True,
            keep_trailing_newline=True
        )

    def configure(self, config: DocumentationConfigModel):
        self.config = config

    def register(self, generator: DocumentationGenerator):
        self.generators.append(generator)

    def write_file(self, file: Path, template: str, **attrs):
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(
            self._jinja_env.get_template(template).render(
                config=self.config,
                root="../" * (len(file.relative_to(self.config.out).parents) - 1),
                **attrs
            )
        )

    def generate(self, ast: list[BaseType], clean: bool = False):
        if clean:
            shutil.rmtree(self.config.out, ignore_errors=True)

