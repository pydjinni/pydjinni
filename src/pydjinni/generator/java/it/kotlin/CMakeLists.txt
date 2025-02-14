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

project(PyDjinniKotlin_IntegrationTesting C CXX)

find_program(KOTLINC_EXECUTABLE kotlinc REQUIRED)
maven_add(annotations GROUP org.jetbrains VERSION 26.0.2)
set(COROUTINE_VERSION 1.10.1)
maven_add(kotlinx-coroutines-core GROUP org.jetbrains.kotlinx VERSION ${COROUTINE_VERSION})
maven_add(kotlinx-coroutines-core-jvm GROUP org.jetbrains.kotlinx VERSION ${COROUTINE_VERSION})
maven_add(kotlinx-coroutines-test GROUP org.jetbrains.kotlinx VERSION ${COROUTINE_VERSION})
maven_add(kotlinx-coroutines-test-jvm GROUP org.jetbrains.kotlinx VERSION ${COROUTINE_VERSION})

function(kotlin_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
            # options
            ""
            # one-value keywords
            ""
            # multi-value keywords
            "SOURCES;JAVA_SOURCES;OPTIONS"
            # args
            ${ARGN}
    )
    set(JNI_TARGET_NAME ${TEST_CASE_NAME}KotlinJni)
    set(JAVA_TARGET_NAME ${TEST_CASE_NAME}KotlinJava)
    set(KOTLIN_TARGET_NAME ${TEST_CASE_NAME}Kotlin)

    implement_test_case(${TEST_CASE_NAME} LANGUAGE java OPTIONS
            ${TEST_CASE_OPTIONS}
            generate.java.out=${CMAKE_CURRENT_LIST_DIR}/generated/java
            generate.java.nullable_annotation=@org.jetbrains.annotations.Nullable
            generate.java.nonnull_annotation=@org.jetbrains.annotations.NotNull
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
    add_library(test::jni::kotlin::${TEST_CASE_NAME} ALIAS ${JNI_TARGET_NAME})

    add_jar(${JAVA_TARGET_NAME}
        OUTPUT_NAME ${TEST_CASE_NAME}
        SOURCES
            ${java_GENERATED_SOURCES}
            ${TEST_CASE_JAVA_SOURCES}
        INCLUDE_JARS
            ${annotations_JAR}
    )
    set_target_properties(${JAVA_TARGET_NAME} PROPERTIES FOLDER "it/${TEST_CASE_NAME}")
    add_dependencies(${JAVA_TARGET_NAME} ${JNI_TARGET_NAME})
    get_target_property(JAVA_JAR_FILE ${JAVA_TARGET_NAME} JAR_FILE)

    set(KOTLIN_JAR_FILE ${CMAKE_CURRENT_BINARY_DIR}/${KOTLIN_TARGET_NAME}.jar)

    if(WIN32)
        set(CLASSPATH_SEPARATOR "\\;")
    else()
        set(CLASSPATH_SEPARATOR ":")
    endif()

    add_custom_command(
        OUTPUT ${KOTLIN_JAR_FILE}
        COMMAND ${KOTLINC_EXECUTABLE}
            -include-runtime
            -classpath \"${JAVA_JAR_FILE}${CLASSPATH_SEPARATOR}${junit-platform-console-standalone_JAR}${CLASSPATH_SEPARATOR}${annotations_JAR}${CLASSPATH_SEPARATOR}${kotlinx-coroutines-core_JAR}${CLASSPATH_SEPARATOR}${kotlinx-coroutines-core-jvm_JAR}${CLASSPATH_SEPARATOR}${kotlinx-coroutines-test_JAR}${CLASSPATH_SEPARATOR}${kotlinx-coroutines-test-jvm_JAR}\"
            -d ${KOTLIN_JAR_FILE}
            ${TEST_CASE_SOURCES}
        DEPENDS ${TEST_CASE_SOURCES}
        COMMENT "Compiling Kotlin code to JAR"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )
    add_custom_target(${KOTLIN_TARGET_NAME} ALL DEPENDS ${KOTLIN_JAR_FILE})
    add_dependencies(${KOTLIN_TARGET_NAME} ${JAVA_TARGET_NAME})
    add_test(NAME Kotlin.${TEST_CASE_NAME} COMMAND ${Java_JAVA_EXECUTABLE}
            -Xcheck:jni
            -Djava.library.path=$<TARGET_FILE_DIR:test::jni::kotlin::${TEST_CASE_NAME}>
            -jar ${junit-platform-console-standalone_JAR}
            --class-path=${JAVA_JAR_FILE}
            --class-path=${KOTLIN_JAR_FILE}
            --class-path=${kotlinx-coroutines-core_JAR}
            --class-path=${kotlinx-coroutines-core-jvm_JAR}
            --class-path=${kotlinx-coroutines-test_JAR}
            --class-path=${kotlinx-coroutines-test-jvm_JAR}
            --scan-classpath
            --disable-banner
            --exclude-engine=junit-vintage
            --exclude-engine=junit-platform-suite
    )
endfunction()

add_subdirectory(async)
add_subdirectory(enum)
add_subdirectory(error)
add_subdirectory(flags)
add_subdirectory(function)
add_subdirectory(interface)
add_subdirectory(namespace)
add_subdirectory(record)
