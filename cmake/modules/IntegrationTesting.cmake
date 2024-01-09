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

define_property(TARGET
        PROPERTY PYDJINNI_INTERFACE
        BRIEF_DOCS "The pydjinni IDL file that was used when generating the targets interface")
define_property(TARGET
        PROPERTY PYDJINNI_OPTIONS
        BRIEF_DOCS "The pydjinni options that where applied when generating the targets interface")

option(ABORT_ON_FAILED_PRECONDITION "If disabled, failed preconditions will only produce a warning." ON)

find_program(DIFF_EXECUTABLE diff)

function(compare_files)
    cmake_parse_arguments(COMPARE
            # options
            ""
            # one-value keywords
            "SOURCE;TARGET"
            # multi-value keywords
            ""
            # args
            ${ARGN}
    )
    file(GLOB_RECURSE EXPECTED_GENERATED_FILES RELATIVE ${COMPARE_SOURCE} ${COMPARE_SOURCE}/*)
    foreach(EXPECTED_FILE ${EXPECTED_GENERATED_FILES})
        file(TO_CMAKE_PATH ${COMPARE_SOURCE}/${EXPECTED_FILE} SOURCE_FILE)
        file(TO_CMAKE_PATH ${COMPARE_TARGET}/${EXPECTED_FILE} TARGET_FILE)
        execute_process(
            COMMAND
                ${CMAKE_COMMAND}
                -E compare_files
                ${SOURCE_FILE}
                ${TARGET_FILE}
            RESULT_VARIABLE
                COMPARE_RESULT
        )
        if(NOT COMPARE_RESULT EQUAL 0)
            if(DIFF_EXECUTABLE)
                message(STATUS "Difference between ${TARGET_FILE} and ${SOURCE_FILE}")
                execute_process(
                    COMMAND
                        ${DIFF_EXECUTABLE}
                        ${SOURCE_FILE}
                        ${TARGET_FILE}
                )
            endif()
            if(ABORT_ON_FAILED_PRECONDITION)
                set(MESSAGE_MODE SEND_ERROR)
            else()
                set(MESSAGE_MODE WARNING)
            endif()
            message(${MESSAGE_MODE} "Precondition failed: Generated output ${TARGET_FILE} is different from expectations: ${SOURCE_FILE}")
        endif()
    endforeach()
endfunction()

function(define_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
        # options
        ""
        # one-value keywords
        "INTERFACE"
        # multi-value keywords
        "OPTIONS;SOURCES"
        # args
        ${ARGN}
        )

    list(APPEND TEST_CASE_OPTIONS
        generate.cpp.out.header=generated/include/cpp
        generate.cpp.out.source=generated/src/cpp
    )

    pydjinni_generate(${TEST_CASE_INTERFACE} CLEAN
        LANGUAGES cpp
        CONFIG None
        OPTIONS
            ${TEST_CASE_OPTIONS}
    )
    compare_files(SOURCE ${CMAKE_CURRENT_LIST_DIR}/expected TARGET ${CMAKE_CURRENT_LIST_DIR}/generated)
    set(BASE_LIB_NAME ${TEST_CASE_NAME}Base)
    add_library(${BASE_LIB_NAME} STATIC
            ${cpp_GENERATED_HEADERS}
            ${cpp_GENERATED_SOURCES}
            ${TEST_CASE_SOURCES}
    )
    target_include_directories(${BASE_LIB_NAME} PUBLIC ${cpp_INCLUDE_DIR})
    target_compile_features(${BASE_LIB_NAME} PUBLIC cxx_std_20)
    add_library(test::${TEST_CASE_NAME} ALIAS ${BASE_LIB_NAME})
    set_target_properties(${BASE_LIB_NAME}
        PROPERTIES
            PYDJINNI_INTERFACE "${TEST_CASE_INTERFACE}"
            PYDJINNI_OPTIONS "${TEST_CASE_OPTIONS}"
            POSITION_INDEPENDENT_CODE ON
    )

endfunction()

macro(implement_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
        # options
        ""
        # one-value keywords
        "LANGUAGE"
        # multi-value keywords
        "OPTIONS"
        # args
        ${ARGN}
    )
    get_target_property(TEST_CASE_INTERFACE test::${TEST_CASE_NAME} PYDJINNI_INTERFACE)
    get_target_property(TEST_CASE_PARENT_OPTIONS test::${TEST_CASE_NAME} PYDJINNI_OPTIONS)
    get_target_property(TEST_CASE_WORKING_DIRECTORY test::${TEST_CASE_NAME} SOURCE_DIR)
    pydjinni_generate(${TEST_CASE_INTERFACE} CLEAN
        LANGUAGES ${TEST_CASE_LANGUAGE}
        CONFIG None
        OPTIONS ${TEST_CASE_PARENT_OPTIONS} ${TEST_CASE_OPTIONS}
        WORKING_DIRECTORY ${TEST_CASE_WORKING_DIRECTORY}
    )
endmacro()
