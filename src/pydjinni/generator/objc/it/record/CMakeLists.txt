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

objc_test_case(RecordTest
    OPTIONS
        generate.objcpp.namespace=test::record_test::objcpp
    SOURCES
        tests/PrimitiveTypesTests.m
        tests/CollectionTypesTests.m
        tests/OptionalTypesTests.m
        tests/BinaryTypesTests.m
        tests/BaseRecordTests.m
        tests/NestedTypeTests.m
)
target_sources(RecordTestObjc
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include/BaseRecord.h
        ${CMAKE_CURRENT_SOURCE_DIR}/src/BaseRecord.m
)
target_include_directories(RecordTestObjc PUBLIC include)
