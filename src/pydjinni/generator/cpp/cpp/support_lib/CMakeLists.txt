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

cmake_minimum_required(VERSION 3.10)

project(PyDjinniCpp_SupportLib CXX)

add_library(cpp_support_lib INTERFACE)
target_include_directories(cpp_support_lib INTERFACE include)
target_link_libraries(cpp_support_lib INTERFACE support_lib::common)
add_library(support_lib::cpp ALIAS cpp_support_lib)

if(BUILD_TESTING)
    add_executable(cpp_support_lib_tests
            tests/test_coroutine.cpp
    )

    target_link_libraries(cpp_support_lib_tests
        PRIVATE
            support_lib::cpp
            Catch2::Catch2WithMain
    )

    catch_discover_tests(cpp_support_lib_tests DISCOVERY_MODE PRE_TEST)
endif()
