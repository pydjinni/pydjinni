# Copyright 2025 jothepro
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

project(PyDjinniIntegrationTestNotNull CXX)

FetchContent_Declare(GSL
        GIT_REPOSITORY https://github.com/microsoft/GSL
        GIT_TAG v4.1.0
        GIT_SHALLOW ON
)

FetchContent_MakeAvailable(GSL)

define_test_case(NotNullTest
    INTERFACE not_null.pydjinni
    SOURCES
        src/not_null_interface.cpp
        src/not_null_interface_impl.hpp
        src/not_null_interface_impl.cpp
    OPTIONS
        generate.cpp.namespace=test::not_null_test
        generate.cpp.not_null.header=<gsl/pointers>
        generate.cpp.not_null.type=::gsl::not_null
)
target_link_libraries(NotNullTestBase PUBLIC Microsoft.GSL::GSL)
