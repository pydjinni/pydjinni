from pathlib import Path

import pydjinni
from pydjinni_init.templates.target import TemplateTarget, Parameter


class ConanCMakeTarget(TemplateTarget):
    """
    Initializes a CMake project that uses Conan to configure and build the PyDjinni library.
    """
    key = "conan-cmake"
    supported_platforms = ["android", "darwin", "windows"]
    parameters = [
        Parameter(
            key="target",
            name="CMake Target Name",
            description="The CMake build target name",
            default="PyDjinniLib"
        ),
        Parameter(
            key="cpp-namespace",
            name="C++ root namespace:",
            description="The C++ root namespace of the library",
            default="pydjinni::lib"
        ),
        Parameter(
            key="version",
            name="Library Version",
            description="Library package version",
            default="0.0.0"
        )
    ]
    additional_files = {
        Path(pydjinni.__path__[0]) / "cmake" / "modules" / "FindPyDjinni.cmake":
            Path("cmake") / "modules" / "FindPyDjinni.cmake"
    }
