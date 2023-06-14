cmake_minimum_required(VERSION 3.24)

project(PyDjinniJava_SupportLib C CXX)

add_library(jni_support_lib
        src/pydjinni/support.cpp
)

target_include_directories(jni_support_lib PUBLIC include)

target_link_libraries(jni_support_lib PUBLIC support_lib::common JNI::JNI)

add_library(support_lib::jni ALIAS jni_support_lib)
