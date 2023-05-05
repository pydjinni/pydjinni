cmake_minimum_required(VERSION 3.6.0)

project(PyDjinniSupportLib C CXX)

Include(FetchContent)
include(CTest)

option(DJINNI_JNI "Build for Java/JNI interop" OFF)
option(DJINNI_OBJC "Build for Objective-C interop" OFF)

if(BUILD_TESTING)
    FetchContent_Declare(
      Catch2
      GIT_REPOSITORY https://github.com/catchorg/Catch2.git
      GIT_TAG        v3.3.2
    )
    FetchContent_MakeAvailable(Catch2)
    include(Catch)
endif()

add_subdirectory(src/pydjinni/generator)

if(BUILD_TESTING)
    add_subdirectory(it)
endif()
