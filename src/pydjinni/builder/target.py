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
from typing import Generic, TypeVar, get_args

from pydantic import BaseModel

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import ApplicationException
from pydjinni.packaging.architecture import Architecture

BuildConfigModel = TypeVar("BuildConfigModel", bound=BaseModel)


class BuildTarget(ABC, Generic[BuildConfigModel]):
    __build_config_model: type

    def __init_subclass__(cls) -> None:
        generic_types = get_args(cls.__orig_bases__[0])  # type: ignore
        assert (
            len(generic_types) > 0
        ), "A BuildTarget implementation must specify a build config model as generic parameter"
        cls.__build_config_model = generic_types[0]

    class BuildException(ApplicationException, code=180):
        """Build step failed"""

    key: str
    """
    The name of the builder. Will be used as configuration key.
    """

    def __init__(self, config_model_builder: ConfigModelBuilder):
        self.config: BuildConfigModel
        config_model_builder.add_builder_config(self.key, self.__build_config_model)

    def configure(self, config: BuildConfigModel):
        self.config: BuildConfigModel = config

    @abstractmethod
    def build(self, build_dir: Path, platform: str, build_type: str, architecture: Architecture) -> Path: ...
