import inspect
import shutil
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from pydjinni.config.config_model_builder import ConfigModelBuilder
from .architecture import Architecture
from .packaging_config import PackageBaseConfig
from .platform import Platform
from pydjinni.builder import BuildTarget


class PackageTarget(ABC):
    @abstractmethod
    @cached_property
    def key(self) -> str:
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
            build_path = self.config.out / self.config.configuration / 'build' / self.key / 'platforms' / target / arch
            if clean and build_path.exists():
                shutil.rmtree(build_path)
            build_artifacts[arch] = build_strategy.build(
                build_dir=build_path,
                platform=target,
                build_type=self.config.configuration,
                architecture=arch
            )
        self._build_artifacts[target] = build_artifacts
        self.after_build(target, architectures)

    def after_build(self, target: str, architectures: set[Architecture]):
        pass

    def package(self, clean: bool = False) -> Path:
        """
        Args:
            clean: Whether the packaging should be started from scratch
        Returns:
            Path to the final package that has been created
        """
        if self.package_build_path.exists() and clean:
            shutil.rmtree(self.package_build_path)
        self.package_build_path.mkdir(parents=True, exist_ok=True)
        if self.package_output_path.exists():
            shutil.rmtree(self.package_output_path)
        self.package_output_path.mkdir(parents=True, exist_ok=True)
        for file in self._template_directory.rglob('*'):
            if file.is_file():
                output_file = self.package_build_path / file.relative_to(self._template_directory)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    output_file.write_text(
                        self._jinja_env.get_template(str(file.relative_to(self._template_directory))).render(
                            config=self.config))
                except UnicodeDecodeError:
                    shutil.copy(src=file, dst=output_file)

        self.package_build()

        return self.package_output_path

    @abstractmethod
    def package_build(self):
        pass

    @abstractmethod
    def publish(self):
        pass
