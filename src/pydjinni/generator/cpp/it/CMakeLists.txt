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

catch_discover_tests(${TEST_CASE_NAME}Cpp)

endfunction()

cpp_test_case(RecordTest
    SOURCES
        tests/test_record.cpp
)

cpp_test_case(InterfaceTest
    SOURCES
        tests/test_interface.cpp
)

cpp_test_case(EnumTest
    SOURCES
        tests/test_enum.cpp
)

cpp_test_case(FlagsTest
    SOURCES
        tests/test_flags.cpp
)

cpp_test_case(FunctionTest
    SOURCES
        tests/test_function.cpp
)

cpp_test_case(AsyncTest
    SOURCES
        tests/test_async.cpp
    INCLUDES
        include
)

cpp_test_case(ErrorTest
    SOURCES
        tests/test_error.cpp
    INCLUDES
        include
)

cpp_test_case(NamespaceTest
    SOURCES
        tests/test_namespace.cpp
)
