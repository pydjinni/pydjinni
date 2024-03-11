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
import os
import shutil
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from pydjinni.builder import BuildTarget
from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import ExternalCommandException, FileNotFoundException
from .architecture import Architecture
from .packaging_config import PackageBaseConfig
from .platform import Platform


def copy_directory(src: Path, dst: Path, clean: bool = False):
    prepare(dst, clean)
    try:
        shutil.copytree(src=src, dst=dst, symlinks=True, dirs_exist_ok=True)
    except FileNotFoundError as e:
        raise FileNotFoundException(Path(e.filename))


def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy(src, dst)
    except FileNotFoundError as e:
        raise FileNotFoundException(e.filename)


def prepare(directory: Path, clean: bool = False):
    """
    prepares a directory for later use. Makes sure the directory exists, and cleans it if requested

    Args:
        directory: the directory that should be prepared
        clean: whether the directory should be cleaned if it may already contain files
    """
    if clean and directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)


def execute(command: str | Path, arguments: list[str], working_dir: Path = Path(os.getcwd())) -> int:
    cwd = os.getcwd()
    os.chdir(working_dir)
    if shutil.which(command):
        full_command = f'{command} {" ".join([str(argument) for argument in arguments])}'
        result = os.system(full_command)
        if result != 0:
            raise ExternalCommandException(full_command)
        os.chdir(cwd)
        return result
    else:
        os.chdir(cwd)
        raise ExternalCommandException(f"Unknown command {command}")


class PackageTarget(ABC):

    @abstractmethod
    @cached_property
    def key(self) -> str:
        """
        The name of the package plugin. Will be used as configuration key.
        """
        pass

    @abstractmethod
    @cached_property
    def publish_config_model(self) -> type[BaseModel]:
        pass

    @abstractmethod
    @cached_property
    def platforms(self) -> dict[Platform, list[Architecture]]:
        """
        Dictionary of supported platforms and architectures
        """

    @cached_property
    def package_output_path(self) -> Path:
        return self.config.out / self.config.configuration / "package" / self.key

    @cached_property
    def package_build_path(self) -> Path:
        return self.config.out / self.config.configuration / 'build' / self.key / 'package'

    @cached_property
    def build_path(self) -> Path:
        return self.config.out / self.config.configuration / 'build' / self.key / 'platforms'

    def __init__(
            self,
            config_model_builder: ConfigModelBuilder):
        self.config: PackageBaseConfig | None = None
        self._build_artifacts: dict[str, dict[Architecture, Path]] = {}
        field_kwargs = {platform: (list[Architecture],
                                   FieldInfo(
                                       description=f"List of targeted architectures. Supported: `{'`, `'.join(architectures)}`"))
                        for
                        platform, architectures in self.platforms.items()}
        config_model_builder.add_package_config(self.key, create_model(
            f"{self.key}_config",
            __doc__=inspect.cleandoc(self.__doc__),
            publish=(self.publish_config_model, None),
            platforms=(create_model(
                f"{self.key}_platform_config",
                **field_kwargs
            ), FieldInfo(
                description="Configuration of target platforms that should be included in the package."
            ))
        ))
        self._template_directory = Path(inspect.getfile(self.__class__)).parent / "template"
        self._jinja_env = Environment(
            loader=FileSystemLoader(self._template_directory),
            keep_trailing_newline=True
        )

    def configure(self, config: PackageBaseConfig):
        self.config = config

    def build(self, build_strategy: BuildTarget, target: str, architectures: set[Architecture], clean: bool = False):
        build_architectures = architectures or getattr(getattr(self.config, self.key).platforms, target)
        build_artifacts = {}
        for arch in build_architectures:
            build_path = self.build_path / target / arch
            prepare(build_path, clean)
            build_artifacts[arch] = build_strategy.build(
                build_dir=build_path,
                platform=target,
                build_type=self.config.configuration,
                architecture=arch
            )
        self._build_artifacts[target] = build_artifacts
        self.after_build(target, architectures)

    def after_build(self, target: str, architectures: set[Architecture]):
        """
        Implement this method to add additional postprocessing step to the build output that was produced by the
        configured build system.
        """
        pass

    def package(self, clean: bool = False) -> Path:
        """
        Args:
            clean: Whether the packaging should be started from scratch
        Returns:
            Path to the final package that has been created
        """
        prepare(self.package_build_path, clean)
        prepare(self.package_output_path, True)
        for file in self._template_directory.rglob('*'):
            if file.is_file():
                output_file = self.package_build_path / file.relative_to(self._template_directory)
                prepare(output_file.parent)
                try:
                    print(str(file.relative_to(self._template_directory).as_posix()))
                    output_file.write_text(
                        self._jinja_env.get_template(str(file.relative_to(self._template_directory).as_posix())).render(
                            config=self.config))
                except UnicodeDecodeError:
                    copy_file(src=file, dst=output_file)

        self.package_build()

        return self.package_output_path

    @abstractmethod
    def package_build(self):
        """
        Implement this method to bundle a package.
        """
        pass

    @abstractmethod
    def publish(self):
        """
        Implement this method to publish the bundled package
        """
        pass
