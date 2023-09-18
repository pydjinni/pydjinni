import os
import shutil
from pathlib import Path

from pydantic import HttpUrl

from pydjinni.packaging.target import PackageTarget
from pydjinni.packaging.architecture import Architecture
from pydjinni.packaging.platform import Platform
from pydjinni.packaging.swiftpackage.publish_config import SwiftpackagePublishConfig


def lipo_combine_framework(input: list[Path], output: Path):
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(src=input[0], dst=output, symlinks=True)
    name_segments = input[0].name.split('.')
    if name_segments[-1] == 'dSYM':
        binary_name = Path('Contents') / 'Resources' / 'DWARF' / name_segments[0]
    else:
        binary_name = Path(input[0].name.split('.')[0])
    input_absolute_paths: list[Path] = [(framework / binary_name).resolve().absolute() for framework in input]
    output_absolute_path = (output / binary_name).resolve()
    os.system(f"lipo -create -output {str(output_absolute_path)} {' '.join([str(path) for path in input_absolute_paths])} ")


class SwiftpackageTarget(PackageTarget):
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
            for artifact in [framework_name, f'{framework_name}.dSYM']:
                lipo_combine_framework(
                    input=[path / artifact for path in build_artifacts_folders],
                    output=merged_output_folder / artifact
                )
            self._build_artifacts[target] = {output_arch: merged_output_folder}

    def package_build(self):
        framework_output_path = self.package_build_path / 'bin'
        xcframework_path = framework_output_path / f'{self.config.target}.xcframework'
        framework_name = f'{self.config.target}.framework'
        if xcframework_path.exists():
            shutil.rmtree(xcframework_path)
        parameters = ""
        for artifacts in self._build_artifacts.values():
            for path in artifacts.values():
                parameters += f'-framework {str((path / framework_name).absolute())} '
                parameters += f'-debug-symbols {str((path / f"{framework_name}.dSYM").absolute())} '
        os.system(f"xcodebuild -create-xcframework -output { str(xcframework_path.absolute()) } {parameters}")
        shutil.copytree(src=self.package_build_path, dst=self.package_output_path, dirs_exist_ok=True)

    def publish(self):
        git_repository_path = self.config.out / self.config.configuration / 'build' / self.key / 'package_repository'
        cwd = os.getcwd()
        if git_repository_path.exists():
            os.chdir(git_repository_path)
            os.system(f"git checkout {self.config.swiftpackage.publish.branch}")
            os.system("git pull")
        else:
            repository: HttpUrl = self.config.swiftpackage.publish.repository
            os.system(f"git clone https://{self.config.swiftpackage.publish.username}:{self.config.swiftpackage.publish.password}@{repository.host}{repository.path} {git_repository_path}")
            os.chdir(git_repository_path)
            os.system(f"git checkout {self.config.swiftpackage.publish.branch}")
        os.chdir(cwd)
        shutil.copytree(src=self.package_build_path, dst=git_repository_path, dirs_exist_ok=True)
        version = (self.package_build_path / "VERSION").read_text()
        os.chdir(git_repository_path)
        os.system("git add .")
        os.system(f'git commit -m "version {version}"')
        os.system(f'git tag {version}')
        os.system("git push")
        os.system("git push --tags")
        os.chdir(cwd)
