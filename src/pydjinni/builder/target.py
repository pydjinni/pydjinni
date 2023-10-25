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

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import ApplicationException
from pydjinni.packaging.architecture import Architecture

BuildConfigModel = TypeVar("BuildConfigModel", bound=BaseModel)


class BuildTarget(ABC):
    class BuildException(ApplicationException, code=180):
        """Build step failed"""

    @property
    @abstractmethod
    def key(self) -> str:
        """
        The name of the builder. Will be used as configuration key.
        """
        pass

    @property
    @abstractmethod
    def config_model(self) -> type[BuildConfigModel]:
        """
        The Pydantic model that defines the configuration options for the builder.

        The model will automatically be registered in the system and is then available in the documentation and as part
        of the  JSON-Schema for the configuration file.
        """
        pass

    def __init__(
            self,
            config_model_builder: ConfigModelBuilder):
        self.config: BuildConfigModel | None = None
        config_model_builder.add_builder_config(self.key, self.config_model)

    def configure(self, config: BuildConfigModel):
        self.config = config

    @abstractmethod
    def build(self, build_dir: Path, platform: str, build_type: str, architecture: Architecture) -> Path:
        ...
