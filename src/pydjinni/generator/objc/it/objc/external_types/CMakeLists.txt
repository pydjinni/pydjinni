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

file(GLOB_RECURSE EXTERNAL_TYPES_OBJC_SOURCES "generated/export/src/objc/*.m")
file(GLOB_RECURSE EXTERNAL_TYPES_OBJCPP_SOURCES "generated/export/src/objcpp/*.mm")

objc_test_case(ExternalTypesTest
    OPTIONS
        generate.objcpp.namespace=test::external_types::objcpp
    SOURCES
        tests/ExternalTypesTests.m
)
target_sources(ExternalTypesTestObjc PUBLIC ${EXTERNAL_TYPES_OBJC_SOURCES} ${EXTERNAL_TYPES_OBJCPP_SOURCES})
target_include_directories(ExternalTypesTestObjc PUBLIC generated/export/include/objc generated/export/include/objcpp)
