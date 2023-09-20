import os

from pydjinni.packaging.target import PackageTarget, copy_file, prepare, execute
from pydjinni.packaging.aar.publish_config import AndroidArchivePublishConfig
from pydjinni.packaging.architecture import Architecture
from pydjinni.packaging.platform import Platform


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

    def package_build(self, clean: bool = False):
        jar_name = f'{self.config.target}.jar'
        so_name = f'lib{self.config.target}.so'
        for artifacts in self._build_artifacts.values():
            for arch, path in artifacts.items():
                copy_file(src=path / jar_name, dst=self.package_build_path / 'libs' / jar_name)
                copy_file(src=path / so_name, dst=self.package_build_path / 'src' / 'main' / 'jniLibs' / self.architecture_mapping[arch] / so_name)
        gradlew_path = self.package_build_path / "gradlew"
        os.chmod(gradlew_path, os.stat(gradlew_path).st_mode | 0o111) # make gradlew executable
        execute("./gradlew", ["assembleRelease"], working_dir=self.package_build_path)
        copy_file(src=self.package_build_path / 'build' / 'outputs' / 'aar' / f'{self.config.target}-release.aar', dst=self.package_output_path / f'{self.config.target}.aar')

    def publish(self):
        execute("./gradlew", [
            "publishReleasePublicationToRemoteRepository",
            f"-PremoteUsername={self.config.aar.publish.username}",
            f"-PremotePassword={self.config.aar.publish.password}"
        ], working_dir=self.package_build_path)
