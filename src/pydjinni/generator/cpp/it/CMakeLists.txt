# Copyright 2023 - 2025 jothepro
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

project(PyDjinniCpp_IntegrationTesting CXX)

function(cpp_test_case TEST_CASE_NAME)

    cmake_parse_arguments(TEST_CASE
            # options
            ""
            # one-value keywords
            ""
            # multi-value keywords
            "SOURCES;INCLUDES"
            # args
            ${ARGN}
            )
    add_executable(${TEST_CASE_NAME}Cpp
        ${TEST_CASE_SOURCES}
    )

    target_link_libraries(${TEST_CASE_NAME}Cpp
        PRIVATE
            Catch2::Catch2WithMain
            test::${TEST_CASE_NAME}
    )
    target_include_directories(${TEST_CASE_NAME}Cpp
        PRIVATE
            ${TEST_CASE_INCLUDES}
    )

    set_target_properties(${TEST_CASE_NAME}Cpp
        PROPERTIES
            FOLDER "it/${TEST_CASE_NAME}"
    )

catch_discover_tests(${TEST_CASE_NAME}Cpp TEST_PREFIX Cpp. DISCOVERY_MODE PRE_TEST)

endfunction()

add_subdirectory(record)
add_subdirectory(interface)
add_subdirectory(enum)
add_subdirectory(flags)
add_subdirectory(function)
add_subdirectory(async)
add_subdirectory(namespace)
add_subdirectory(not_null)
