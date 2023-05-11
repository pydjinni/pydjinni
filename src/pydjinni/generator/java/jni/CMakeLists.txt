cmake_minimum_required(VERSION 3.24)

project(PyDjinniJniSupportLib C CXX)

set(JAVA_AWT_LIBRARY NotNeeded)
set(JAVA_AWT_INCLUDE_PATH NotNeeded)
find_package(JNI REQUIRED QUIET)

add_library(jni_support_lib
        support_lib/src/pydjinni/support.cpp
)

target_include_directories(jni_support_lib PUBLIC support_lib/include)

target_link_libraries(jni_support_lib PUBLIC support_lib::common JNI::JNI)

add_library(support_lib::jni ALIAS jni_support_lib)
