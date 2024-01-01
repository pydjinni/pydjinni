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

from pathlib import Path

from pydantic import AnyUrl, HttpUrl
from pydjinni.packaging.architecture import Architecture
from pydjinni.packaging.platform import Platform
from pydjinni.packaging.swiftpackage.publish_config import SwiftpackagePublishConfig
from pydjinni.packaging.target import PackageTarget, prepare, copy_directory, execute


def lipo_combine_framework(input: list[Path], output: Path):
    copy_directory(src=input[0], dst=output, clean=True)

    name_segments = input[0].name.split('.')
    if name_segments[-1] == 'dSYM':
        binary_name = Path('Contents') / 'Resources' / 'DWARF' / name_segments[0]
    else:
        binary_name = Path(input[0].name.split('.')[0])
    input_absolute_paths: list[Path] = [(framework / binary_name).resolve().absolute() for framework in input]
    output_absolute_path = (output / binary_name).resolve()
    execute("lipo", arguments=[
        "-create",
        f"-output {str(output_absolute_path)}",
        *[str(path) for path in input_absolute_paths]
    ])


class SwiftpackageTarget(PackageTarget):
    """
    Swift package
    """
    key = "swiftpackage"
    platforms = {
        Platform.macos: [Architecture.x86_64, Architecture.armv8],
        Platform.ios: [Architecture.armv8],
        Platform.ios_simulator: [Architecture.x86_64, Architecture.armv8]
    }
    publish_config_model = SwiftpackagePublishConfig

    def after_build(self, target: str, architectures: list[Architecture]):
        build_artifacts_folders = self._build_artifacts[target].values()
        if len(build_artifacts_folders) > 1:
            output_arch = '_'.join(self._build_artifacts[target].keys())
            framework_name = f'{self.config.target}.framework'
            merged_output_folder = self.config.out / self.config.configuration / 'build' / 'swiftpackage' / 'platforms' / target / output_arch / 'dist'

            lipo_combine_framework(
                input=[path / framework_name for path in build_artifacts_folders],
                output=merged_output_folder / framework_name
            )
            dsym_name = f'{framework_name}.dSYM'
            dsym_input = [path / dsym_name for path in build_artifacts_folders if (path / dsym_name).exists()]
            if dsym_input:
                lipo_combine_framework(
                    input=dsym_input,
                    output=merged_output_folder / dsym_name
                )

            self._build_artifacts[target] = {output_arch: merged_output_folder}

    def package_build(self):
        framework_output_path = self.package_build_path / 'bin'
        xcframework_path = framework_output_path / f'{self.config.target}.xcframework'
        framework_name = f'{self.config.target}.framework'
        prepare(xcframework_path, clean=True)
        parameters = []
        for artifacts in self._build_artifacts.values():
            for path in artifacts.values():
                parameters.append(f'-framework {str((path / framework_name).absolute())}')
                dsym_path = path / f"{framework_name}.dSYM"
                if dsym_path.exists():
                    parameters.append(f'-debug-symbols {str(dsym_path.absolute())}')
        execute("xcodebuild", [
            "-create-xcframework",
            f"-output {str(xcframework_path.absolute())}",
            *parameters
        ])
        copy_directory(src=self.package_build_path, dst=self.package_output_path, clean=True)

    def publish(self):
        repository: HttpUrl | Path = self.config.swiftpackage.publish.repository
        if isinstance(repository, Path) and not (str(repository).startswith("git@") and repository.suffix == ".git"):
            copy_directory(src=self.package_build_path, dst=repository / self.config.target, clean=True)
        else:
            git_repository_path = self.config.out / self.config.configuration / 'build' / self.key / 'package_repository'
            if git_repository_path.exists():
                execute("git", ["checkout", self.config.swiftpackage.publish.branch], working_dir=git_repository_path)
                execute("git", ["pull"], working_dir=git_repository_path)
            else:
                if isinstance(repository, Path):
                    execute("git", [
                        "clone",
                        repository,
                        git_repository_path
                    ])
                else:
                    execute("git", [
                        "clone",
                        f"{repository.scheme}://{self.config.swiftpackage.publish.username}:{self.config.swiftpackage.publish.password}@{repository.host}{f':{repository.port}' if repository.port else ''}{repository.path}",
                        git_repository_path
                    ])
                execute("git", ["checkout", self.config.swiftpackage.publish.branch], working_dir=git_repository_path)
            (git_repository_path / "Package.swift").unlink()
            prepare(git_repository_path / "bin", clean=True)
            copy_directory(src=self.package_build_path, dst=git_repository_path)
            version = (self.package_build_path / "VERSION").read_text()
            execute("git", ["add", "."], working_dir=git_repository_path)
            execute("git", ["commit", f'-m "version {version}"'], working_dir=git_repository_path)
            execute("git", ["tag", version], working_dir=git_repository_path)
            execute("git", ["push"], working_dir=git_repository_path)
            execute("git", ["push", "--tags"], working_dir=git_repository_path)


