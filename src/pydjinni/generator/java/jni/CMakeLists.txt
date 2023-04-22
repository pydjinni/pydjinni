cmake_minimum_required(VERSION 3.6.0)

project(PyDjinniJniSupportLib C CXX)

add_library(jni_support_lib
        support_lib/src/support.cpp
)

target_include_directories(jni_support_lib PUBLIC support_lib/include)

target_link_libraries(jni_support_lib PUBLIC common_support_lib)
