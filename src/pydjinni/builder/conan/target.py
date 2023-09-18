import shutil
from pathlib import Path

from conan.cli.cli import Cli
from conan.api.conan_api import ConanAPI


from pydjinni.builder.conan.config_model import ConanConfigModel
from pydjinni.builder import BuildTarget
from pydjinni.packaging.architecture import Architecture


class ConanTarget(BuildTarget):
    """
    Conan build target. Uses conan to build the binaries for packaging.
    Expects all library binaries mean for distribution to be in a folder called "dist" in the root of the build folder.

    It is in the responsibility of the underlying build system or the conan configuration to ensure that all outputs
    are copied to the "dist" directory for further processing.
    """

    key = "conan"

    config_model = ConanConfigModel

    def build(self, build_dir: Path, platform: str, build_type: str, architecture: Architecture) -> Path:
        Cli(ConanAPI()).run(['build',
                          '--output-folder', str(build_dir),
                          '--profile:host', f'{self.config.conan.profiles / platform }',
                          '--settings:host', f'build_type={build_type}',
                          '--settings:host', f'arch={architecture}',
                          '--build', 'missing', '.'])
        return build_dir / "dist"
