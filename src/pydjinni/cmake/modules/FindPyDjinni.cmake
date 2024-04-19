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

# FindPyDjinni
# ============
#
# Finds the PyDjinni CMake module that is distributed with the PyDjinni Python wheel.
# Looks up the current installation path of the `pydjinni` Python module and appends the contained
# CMake modules directory to `CMAKE_MODULE_PATH`

include(FindPackageHandleStandardArgs)

execute_process(COMMAND python -c "import pydjinni; print(pydjinni.__path__[0])"
        OUTPUT_STRIP_TRAILING_WHITESPACE
        OUTPUT_VARIABLE PyDjinni_ROOT_DIR)
execute_process(COMMAND python -c "from importlib.metadata import version; print(version('pydjinni'))"
        OUTPUT_STRIP_TRAILING_WHITESPACE
        OUTPUT_VARIABLE PyDjinni_VERSION)
file(TO_CMAKE_PATH ${PyDjinni_ROOT_DIR} PyDjinni_ROOT_DIR)
list(APPEND CMAKE_MODULE_PATH ${PyDjinni_ROOT_DIR}/cmake/modules)
find_package_handle_standard_args(PyDjinni
    VERSION_VAR PyDjinni_VERSION
    REQUIRED_VARS
        PyDjinni_ROOT_DIR
        PyDjinni_VERSION
)
