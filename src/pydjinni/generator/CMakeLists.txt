cmake_minimum_required(VERSION 3.6.0)

project(PyDjinniCommonSupportLib C CXX)

add_library(common_support_lib
        support_lib/src/common.cpp
)

target_include_directories(common_support_lib PUBLIC support_lib/include)

add_library(support_lib::common ALIAS common_support_lib)

add_subdirectory(java/jni)
add_subdirectory(objc/objcpp)

add_executable(common_support_lib_tests
    support_lib/tests/test.cpp
)

target_link_libraries(common_support_lib_tests
    PRIVATE
        support_lib::common
        Catch2::Catch2WithMain
)

catch_discover_tests(common_support_lib_tests)
