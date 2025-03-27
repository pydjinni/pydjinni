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

file(GLOB_RECURSE EXTERNAL_TYPES_CPPCLI_HEADERS "generated/export/include/**/*.hpp")
file(GLOB_RECURSE EXTERNAL_TYPES_CPPCLI_SOURCES "generated/export/src/**/*.cpp")

cppcli_test_case(ExternalTypesTest
    OPTIONS
        generate.cppcli.namespace=Test::ExternalTypes::CppCli
    SOURCES
        tests/ExternalTypesTest.cs
)
target_include_directories(ExternalTypesTestCppCli PRIVATE generated/export/include/cppcli)
target_sources(ExternalTypesTestCppCli PRIVATE ${EXTERNAL_TYPES_CPPCLI_HEADERS} ${EXTERNAL_TYPES_CPPCLI_SOURCES})
