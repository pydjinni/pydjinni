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
from dataclasses import dataclass
from functools import cached_property
from importlib.metadata import version
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pydjinni_init.exceptions import ApplicationException


class UnknownTargetException(ApplicationException, code=120):
    """Unknown packaging target"""

@dataclass
class Parameter:
    key: str
    name: str
    description: str
    default: str = None


class TemplateTarget(ABC):

    @abstractmethod
    @cached_property
    def key(self) -> str:
        """
        The name of the package plugin. Will be used as configuration key.
        """
        pass

    @abstractmethod
    @cached_property
    def supported_platforms(self) -> list[str]:
        """
        A list of target platforms that are supported by the template
        """
        pass

    @abstractmethod
    @cached_property
    def parameters(self) -> list[Parameter]:
        pass

    @abstractmethod
    @cached_property
    def additional_files(self) -> dict[Path, Path]:
        """
        List of additional files not in the templates directory that should be included in the output
        """
        pass

    def __init__(self):
        self._template_directory = Path(inspect.getfile(self.__class__)).parent / "template"
        self._jinja_env = Environment(
            loader=FileSystemLoader(self._template_directory),
            keep_trailing_newline=True
        )

    def template(self, platforms: list[str], parameters: dict[str, str]):
        for platform in platforms:
            if platform not in self.supported_platforms:
                raise UnknownTargetException(platform)
        for file in self._template_directory.rglob('*'):
            if file.is_file():
                output_file = Path().resolve() / file.relative_to(self._template_directory)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    output = self._jinja_env.get_template(
                        str(file.relative_to(self._template_directory).as_posix())).render(
                        pydjinni_version=version('pydjinni'),
                        platforms=platforms,
                        **parameters)
                    if output.strip() != "":
                        output_file.write_text(output)
                except UnicodeDecodeError:
                    shutil.copy(src=file, dst=output_file)
        for file, target in self.additional_files.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src=file, dst=target)
