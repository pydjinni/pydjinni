cmake_minimum_required(VERSION 3.6.0)

project(PyDjinniSupportLib C CXX)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")
Include(FetchContent)
Include(CTest)
Include(PyDjinni)

option(PYDJINNI_JNI "Build for Java/JNI interop" OFF)
option(PYDJINNI_OBJC "Build for Objective-C interop" OFF)

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
