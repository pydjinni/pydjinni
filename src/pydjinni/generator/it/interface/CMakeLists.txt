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

project(PyDjinniIntegrationTestInterface CXX)

define_test_case(InterfaceTest
    INTERFACE interface.pydjinni
    SOURCES
        src/calculator.cpp
        src/calculator_impl.cpp
        src/calculator_impl.hpp
        src/deprecation_test.cpp
        src/optional_interface.cpp
        src/optional_interface_impl.cpp
        src/optional_interface_impl.hpp
    OPTIONS
        generate.cpp.namespace=test::interface_test
)
