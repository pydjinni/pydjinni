# Copyright 2023 - 2024 jothepro
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

cmake_minimum_required(VERSION 3.10)

project(PyDjinniSupportLib C CXX)

option(BUILD_TESTING "Whether testing should be enabled or not" ON)

option(ADDRESS_SANITIZER "Enables address sanitizer" OFF)

if(ADDRESS_SANITIZER)
    add_compile_options(-fsanitize=address)
    add_link_options(-fsanitize=address)
endif()

set(PYDJINNI_LANGUAGE_TARGETS_DEFAULT cpp)
if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    list(APPEND PYDJINNI_LANGUAGE_TARGETS_DEFAULT objc java)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    list(APPEND PYDJINNI_LANGUAGE_TARGETS_DEFAULT java)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    list(APPEND PYDJINNI_LANGUAGE_TARGETS_DEFAULT java)
    list(APPEND PYDJINNI_LANGUAGE_TARGETS_DEFAULT cppcli)
endif()

set(PYDJINNI_LANGUAGE_TARGETS ${PYDJINNI_LANGUAGE_TARGETS_DEFAULT} CACHE STRING "List of languages that should be targeted" )

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/src/pydjinni/cmake/modules")
Include(PyDjinni)
Include(FetchContent)

if(BUILD_TESTING)
    Include(IntegrationTesting)
    enable_testing()
    FetchContent_Declare(
        Catch2
        GIT_REPOSITORY https://github.com/catchorg/Catch2.git
        GIT_TAG        v3.3.2
    )
    FetchContent_MakeAvailable(Catch2)
    include(Catch)
endif()

add_subdirectory(src/pydjinni/generator)
