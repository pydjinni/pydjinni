import os
import shutil
from pathlib import Path

from pydjinni.packaging.target import PackageTarget
from pydjinni.packaging.aar.publish_config import AndroidArchivePublishConfig
from pydjinni.packaging.architecture import Architecture
from pydjinni.packaging.platform import Platform


class AndroidArchiveTarget(PackageTarget):
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

    def package_build(self, clean: bool = False):
        jar_name = f'{self.config.target}.jar'
        so_name = f'lib{self.config.target}.so'
        for artifacts in self._build_artifacts.values():
            for arch, path in artifacts.items():
                jar_destination = self.package_build_path / 'libs'
                jar_destination.mkdir(parents=True, exist_ok=True)
                shutil.copy(src=path / jar_name, dst=self.package_build_path / 'libs')
                so_destination = self.package_build_path / 'src' / 'main' / 'jniLibs' / self.architecture_mapping[arch]
                so_destination.mkdir(parents=True, exist_ok=True)
                shutil.copy(src=path / so_name, dst=so_destination)
        cwd = os.getcwd()
        os.chdir(self.package_build_path)
        os.chmod("gradlew", os.stat("gradlew").st_mode | 0o111)
        os.system("./gradlew assembleRelease")
        os.chdir(cwd)
        shutil.copy(src=self.package_build_path / 'build' / 'outputs' / 'aar' / f'{self.config.target}-release.aar', dst=self.package_output_path / f'{self.config.target}.aar')

    def publish(self):
        cwd = os.getcwd()
        os.chdir(self.package_build_path)
        os.system(f"./gradlew publishReleasePublicationToRemoteRepository -PremoteUsername={self.config.aar.publish.username} -PremotePassword={self.config.aar.publish.password}")
        os.chdir(cwd)
