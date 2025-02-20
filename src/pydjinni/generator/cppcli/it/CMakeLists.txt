# Copyright 2024 - 2025 jothepro
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

project(PyDjinniCppCli_IntegrationTesting CXX CSharp)

find_program(DOTNET_EXECUTABLE dotnet REQUIRED)

foreach( OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES} )
    string( TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG )
    set( CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${CMAKE_BINARY_DIR}/bin )
endforeach()

function(cppcli_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
        # options
        ""
        # one-value keywords
        ""
        # multi-value keywords
        "INCLUDE;SOURCES;OPTIONS"
        # args
        ${ARGN}
    )
    set(CPPCLI_TARGET_NAME ${TEST_CASE_NAME}CppCli)
    set(CS_TARGET_NAME ${TEST_CASE_NAME}Cs)

    implement_test_case(${TEST_CASE_NAME} LANGUAGE cppcli OPTIONS
            ${TEST_CASE_OPTIONS}
            generate.cppcli.out.header=${CMAKE_CURRENT_LIST_DIR}/generated/include/cppcli
            generate.cppcli.out.source=${CMAKE_CURRENT_LIST_DIR}/generated/src/cppcli
            generate.cppcli.nullability_attributes=false
    )
    compare_files(SOURCE ${CMAKE_CURRENT_LIST_DIR}/expected TARGET ${CMAKE_CURRENT_LIST_DIR}/generated)
    add_library(${CPPCLI_TARGET_NAME} SHARED
            ${cppcli_GENERATED_HEADERS}
            ${cppcli_GENERATED_SOURCES}
            )
    target_include_directories(${CPPCLI_TARGET_NAME} PUBLIC ${cppcli_INCLUDE_DIR} ${cppcli_SOURCE_DIR} ${TEST_CASE_INCLUDE})
    target_compile_features(${CPPCLI_TARGET_NAME} PUBLIC cxx_std_20)
    set_target_properties(${CPPCLI_TARGET_NAME} PROPERTIES
        VS_DOTNET_REFERENCES "System;System.Core"
        COMMON_LANGUAGE_RUNTIME ""
        CXX_STANDARD 20
        FOLDER "it/${TEST_CASE_NAME}"
    )
    target_link_options(${CPPCLI_TARGET_NAME} PUBLIC "/INCREMENTAL:NO")
    target_link_libraries(${CPPCLI_TARGET_NAME} PUBLIC test::${TEST_CASE_NAME})
    add_library(test::cppcli::${TEST_CASE_NAME} ALIAS ${CPPCLI_TARGET_NAME})

    add_library(${CS_TARGET_NAME} SHARED
        ${TEST_CASE_SOURCES}
    )

    set_target_properties(${CS_TARGET_NAME}  PROPERTIES
        VS_DOTNET_REFERENCES "System;System.Core"
        VS_PACKAGE_REFERENCES "nunit_4.3.2;NUnit3TestAdapter_4.6.0;Microsoft.NET.Test.Sdk_17.12.0"
        FOLDER "it/${TEST_CASE_NAME}"
    )

    target_link_libraries(${CS_TARGET_NAME} PUBLIC test::cppcli::${TEST_CASE_NAME})

    add_test(NAME CppCli.${TEST_CASE_NAME} COMMAND ${DOTNET_EXECUTABLE}
        test ${CMAKE_BINARY_DIR}/bin/${CS_TARGET_NAME}.dll
    )
endfunction()

add_subdirectory(record)
add_subdirectory(interface)
add_subdirectory(enum)
add_subdirectory(flags)
add_subdirectory(function)
add_subdirectory(async)
add_subdirectory(error)
add_subdirectory(namespace)
