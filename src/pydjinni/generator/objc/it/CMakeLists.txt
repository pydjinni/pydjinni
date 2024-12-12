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

project(PyDjinniObjc_IntegrationTesting OBJC OBJCXX)

find_package(XCTest REQUIRED)

function(objc_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
            # options
            ""
            # one-value keywords
            ""
            # multi-value keywords
            "SOURCES;OPTIONS"
            # args
            ${ARGN}
            )
    set(TEST_LIBRARY_NAME ${TEST_CASE_NAME}Objc)
    set(TEST_BUNDLE_NAME ${TEST_LIBRARY_NAME}TestBundle)
    implement_test_case(${TEST_CASE_NAME} LANGUAGE objc
        OPTIONS
            ${TEST_CASE_OPTIONS}
            generate.objc.type_prefix=TST
            generate.objc.out.header=${CMAKE_CURRENT_LIST_DIR}/generated/include/objc
            generate.objc.out.source=${CMAKE_CURRENT_LIST_DIR}/generated/src/objc
            generate.objcpp.out.header=${CMAKE_CURRENT_LIST_DIR}/generated/include/objcpp
            generate.objcpp.out.source=${CMAKE_CURRENT_LIST_DIR}/generated/src/objcpp
        )
    compare_files(SOURCE ${CMAKE_CURRENT_LIST_DIR}/expected TARGET ${CMAKE_CURRENT_LIST_DIR}/generated)
    add_library(${TEST_LIBRARY_NAME}
        ${objc_GENERATED_HEADERS}
        ${objc_GENERATED_SOURCES}
        ${objcpp_GENERATED_HEADERS}
        ${objcpp_GENERATED_SOURCES}
    )
    target_include_directories(${TEST_LIBRARY_NAME} PUBLIC ${objc_INCLUDE_DIR} ${objcpp_INCLUDE_DIR} ${objcpp_SOURCE_DIR})
    target_compile_options(${TEST_LIBRARY_NAME} PUBLIC "-fobjc-arc")
    target_link_libraries(${TEST_LIBRARY_NAME} PUBLIC test::${TEST_CASE_NAME} "-framework Foundation")
    set_target_properties(${TEST_LIBRARY_NAME} PROPERTIES FOLDER "it/${TEST_CASE_NAME}")
    xctest_add_bundle(${TEST_BUNDLE_NAME} ${TEST_LIBRARY_NAME} ${TEST_CASE_SOURCES})
    set_target_properties(${TEST_BUNDLE_NAME} PROPERTIES FOLDER "it/${TEST_CASE_NAME}")
    xctest_add_test(Objc.${TEST_CASE_NAME} ${TEST_BUNDLE_NAME})
endfunction()

add_subdirectory(enum)
add_subdirectory(flags)
add_subdirectory(record)
add_subdirectory(interface)
add_subdirectory(function)
add_subdirectory(async)
add_subdirectory(error)
