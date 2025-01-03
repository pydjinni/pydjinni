# Copyright 2024 jothepro
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
    """
    Custom configuration parameter required for rendering the template.
    """
    key: str
    name: str
    description: str
    default: str = None


class TemplateTarget(ABC):
    """
    Abstract base class that all template plugins must derive from.
    """

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
        A list of target platforms that are supported by the template.
        Possible values can be defined by the template plugin.
        """
        pass

    @abstractmethod
    @cached_property
    def parameters(self) -> list[Parameter]:
        """
        List of custom parameters that are required for rendering the template.
        Each parameter will be added as mandatory command line option that will prompt for a value if not provided by
        the user in the command call.
        """
        pass

    @abstractmethod
    @cached_property
    def additional_files(self) -> dict[Path, Path]:
        """
        Map of additional files not in the templates directory that should be included in the output.
        The key is the source of the file, the value is the relative output path where the file should be written to.
        """
        pass

    @property
    def template_line_statement_prefix(self) -> str: return "//>"

    @property
    def template_line_comment_prefix(self) -> str: return "///"

    @property
    def template_variable_start_string(self) -> str: return "{{"

    @property
    def template_variable_end_string(self) -> str: return "}}"

    @property
    def template_block_start_string(self) -> str: return "/*>"

    @property
    def template_block_end_string(self) -> str: return "*/"

    @property
    def template_comment_start_string(self) -> str: return "/*#"

    @property
    def template_comment_end_string(self) -> str: return "*/"

    def __init__(self):
        self._template_directory = Path(inspect.getfile(self.__class__)).parent / "template"
        self._jinja_env = Environment(
            loader=FileSystemLoader(self._template_directory),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            line_statement_prefix=self.template_line_statement_prefix,
            line_comment_prefix=self.template_line_comment_prefix,
            variable_start_string=self.template_variable_start_string,
            variable_end_string=self.template_variable_end_string,
            block_start_string=self.template_block_start_string,
            block_end_string=self.template_block_end_string,
            comment_start_string=self.template_comment_start_string,
            comment_end_string=self.template_comment_end_string
        )

    def template(self, output_dir: Path, platforms: list[str], parameters: dict[str, str]):
        for platform in platforms:
            if platform not in self.supported_platforms:
                raise UnknownTargetException(platform)
        for file in self._template_directory.rglob('*'):
            if file.is_file():
                output_file = output_dir.resolve() / file.relative_to(self._template_directory)
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
            (output_dir / target).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src=file, dst=output_dir / target)
