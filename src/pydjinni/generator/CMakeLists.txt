cmake_minimum_required(VERSION 3.6.0)

project(PyDjinniCommonSupportLib C CXX)

add_library(common_support_lib
        support_lib/src/common.cpp
)

target_include_directories(common_support_lib PUBLIC support_lib/include)

add_subdirectory(java/jni)
add_subdirectory(objc/objcpp)
