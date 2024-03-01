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

import os
from functools import cached_property

from pydjinni.packaging.aar.publish_config import AndroidArchivePublishConfig
from pydjinni.packaging.architecture import Architecture
from pydjinni.packaging.platform import Platform
from pydjinni.packaging.target import PackageTarget, copy_file, execute, copy_directory


class AndroidArchiveTarget(PackageTarget):
    """
    Android Archive
    """
    key = "aar"
    platforms = {
        Platform.android: [Architecture.x86, Architecture.x86_64, Architecture.armv7, Architecture.armv8]
    }
    publish_config_model = AndroidArchivePublishConfig

    architecture_mapping = {
        Architecture.x86: "x86",
        Architecture.x86_64: "x86_64",
        Architecture.armv7: "armeabi-v7a",
        Architecture.armv8: "arm64-v8a"
    }

    @cached_property
    def gradlew_path(self):
        return (self.package_build_path / "gradlew").absolute()

    def package_build(self, clean: bool = False):
        so_name = f'lib{self.config.target}.so'
        for artifacts in self._build_artifacts.values():
            for arch, path in artifacts.items():
                copy_directory(src=path / self.config.target, dst=self.package_build_path / 'src' / 'main' / 'java')
                copy_file(src=path / so_name,
                          dst=self.package_build_path / 'src' / 'main' / 'jniLibs' / self.architecture_mapping[
                              arch] / so_name)
        os.chmod(self.gradlew_path, os.stat(self.gradlew_path).st_mode | 0o111)  # make gradlew executable
        execute(self.gradlew_path.absolute(), ["assembleRelease"], working_dir=self.package_build_path)
        copy_file(src=self.package_build_path / 'build' / 'outputs' / 'aar' / f'{self.config.target}-release.aar',
                  dst=self.package_output_path / f'{self.config.target}.aar')

    def publish(self):
        if self.config.aar.publish.maven_registry:
            execute(self.gradlew_path, [
                "publishReleasePublicationToRemoteRepository",
                f"-PremoteUsername={self.config.aar.publish.username}",
                f"-PremotePassword={self.config.aar.publish.password}"
            ], working_dir=self.package_build_path)
        else:
            execute("./gradlew", [
                "publishReleasePublicationToMavenLocal"
            ], working_dir=self.package_build_path)
