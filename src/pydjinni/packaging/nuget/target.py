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
from pathlib import Path

from pydjinni.exceptions import ExternalCommandException
from pydjinni.packaging.architecture import Architecture
from pydjinni.packaging.nuget.publish_config import NuGetPublishConfig
from pydjinni.packaging.platform import Platform
from pydjinni.packaging.target import PackageTarget, copy_file, execute, copy_directory


class NuGetTarget(PackageTarget):
    """
    NuGet Package
    """
    key = "nuget"
    platforms = {
        Platform.windows: [Architecture.x86, Architecture.x86_64, Architecture.armv7, Architecture.armv8]
    }
    publish_config_model = NuGetPublishConfig

    architecture_mapping = {
        Architecture.x86: "win-x86",
        Architecture.x86_64: "win-x64",
        Architecture.armv7: "win-arm",
        Architecture.armv8: "win-arm64"
    }

    def package_build(self, clean: bool = False):
        ref_copied = False
        pdb_exists = False
        for artifacts in self._build_artifacts.values():
            for arch, path in artifacts.items():
                if not ref_copied:
                    copy_directory(
                        src=path,
                        dst=self.package_build_path / 'ref' / self.config.nuget.publish.net_version
                    )
                    pdb_exists = (path / f"{self.config.target}.pdb").exists()
                    ref_copied = True

                copy_directory(
                    src=path,
                    dst=self.package_build_path / 'runtimes' / self.architecture_mapping[
                        arch] / 'lib' / self.config.nuget.publish.net_version
                )
        if self.config.nuget.publish.readme:
            copy_file(src=self.config.nuget.publish.readme, dst=self.package_build_path / "README.md")
        execute("nuget", [
            "pack", "Package.nuspec",
            "-Properties", f"Configuration={self.config.configuration}",
            "-Properties", "NoWarn=NU5131",  # see https://github.com/NuGet/Home/discussions/11097
            "-OutputDirectory", f"{self.package_output_path.absolute()}",
        ] + (["-Symbols"] if pdb_exists else []), working_dir=self.package_build_path)

    def publish(self):
        local = isinstance(self.config.nuget.publish.source, Path)
        if not local:
            try:
                execute("nuget", [
                    "sources", "update",
                    "-Name", "nuget_server",
                    "-Source", self.config.nuget.publish.source,
                    "-username", self.config.nuget.publish.username,
                    "-password", self.config.nuget.publish.password
                ], working_dir=self.package_output_path)
            except ExternalCommandException:
                execute("nuget", [
                    "sources", "add",
                    "-Name", "nuget_server",
                    "-Source", self.config.nuget.publish.source,
                    "-username", self.config.nuget.publish.username,
                    "-password", self.config.nuget.publish.password
                ], working_dir=self.package_output_path)
        symbols_nupkg = f"{self.config.target}.{self.config.version}.symbols.nupkg"
        nupkg = symbols_nupkg if (self.package_output_path / symbols_nupkg).exists() else f"{self.config.target}.{self.config.version}.nupkg"
        source = ["nuget_server", "-ApiKey", self.config.nuget.publish.password] if not local else [self.config.nuget.publish.source.absolute()]
        execute("nuget", [
            "push", nupkg,
            "-Source"
        ] + source, working_dir=self.package_output_path)
