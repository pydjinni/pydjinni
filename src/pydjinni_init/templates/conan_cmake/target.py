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

import pydjinni
from pydjinni_init.templates.target import TemplateTarget, Parameter


class ConanCMakeTarget(TemplateTarget):
    """
    Initializes a CMake project that uses Conan to configure and build a PyDjinni cross-platform library.
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
    template_line_statement_prefix = "#>"
