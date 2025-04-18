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

project(PyDjinniJava_IntegrationTesting C CXX)

function(java_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
        # options
        ""
        # one-value keywords
        ""
        # multi-value keywords
        "SOURCES;TEST_SOURCES;OPTIONS"
        # args
        ${ARGN}
    )
    set(JNI_TARGET_NAME ${TEST_CASE_NAME}Jni)
    set(JAVA_TARGET_NAME ${TEST_CASE_NAME}Java)

    implement_test_case(${TEST_CASE_NAME} LANGUAGE java OPTIONS
            ${TEST_CASE_OPTIONS}
            generate.java.out=${CMAKE_CURRENT_LIST_DIR}/generated/java
            generate.jni.out.header=${CMAKE_CURRENT_LIST_DIR}/generated/include/jni
            generate.jni.out.source=${CMAKE_CURRENT_LIST_DIR}/generated/src/jni
            generate.java.native_lib=${JNI_TARGET_NAME})
    compare_files(SOURCE ${CMAKE_CURRENT_LIST_DIR}/expected TARGET ${CMAKE_CURRENT_LIST_DIR}/generated)
    add_library(${JNI_TARGET_NAME} SHARED
            ${jni_GENERATED_HEADERS}
            ${jni_GENERATED_SOURCES}
            )
    target_include_directories(${JNI_TARGET_NAME} PUBLIC ${jni_INCLUDE_DIR} ${jni_SOURCE_DIR})
    target_link_libraries(${JNI_TARGET_NAME} PUBLIC JNI::JNI test::${TEST_CASE_NAME})
    set_target_properties(${JNI_TARGET_NAME} PROPERTIES FOLDER "it/${TEST_CASE_NAME}")
    add_library(test::jni::java::${TEST_CASE_NAME} ALIAS ${JNI_TARGET_NAME})

    add_jar(${JAVA_TARGET_NAME}
        OUTPUT_NAME ${TEST_CASE_NAME}
        SOURCES
            ${java_GENERATED_SOURCES}
            ${TEST_CASE_TEST_SOURCES}
            ${TEST_CASE_SOURCES}
        INCLUDE_JARS
            ${junit-platform-console-standalone_JAR}
    )
    create_javadoc(${JAVA_TARGET_NAME}
        FILES ${java_GENERATED_SOURCES} ${TEST_CASE_SOURCES}
    )
    set_target_properties(${JAVA_TARGET_NAME} PROPERTIES FOLDER "it/${TEST_CASE_NAME}")
    set_target_properties(${JAVA_TARGET_NAME}_javadoc PROPERTIES FOLDER "it/${TEST_CASE_NAME}")
    add_dependencies(${JAVA_TARGET_NAME} ${JNI_TARGET_NAME} ${JAVA_TARGET_NAME}_javadoc)
    get_target_property(TEST_JAR_FILE ${JAVA_TARGET_NAME} JAR_FILE)
    add_test(NAME Java.${TEST_CASE_NAME} COMMAND ${Java_JAVA_EXECUTABLE}
        -Xcheck:jni
        -Djava.library.path=$<TARGET_FILE_DIR:test::jni::java::${TEST_CASE_NAME}>
        -jar ${junit-platform-console-standalone_JAR}
        --class-path=${TEST_JAR_FILE}
        --scan-classpath
        --disable-banner
        --exclude-engine=junit-vintage
        --exclude-engine=junit-platform-suite
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
add_subdirectory(external_types)
