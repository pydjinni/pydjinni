cmake_minimum_required(VERSION 3.6.0)

project(PyDjinniSupportLib C CXX)

option(DJINNI_JNI "Build for Java/JNI interop" OFF)
option(DJINNI_OBJC "Build for Objective-C interop" OFF)

Include(FetchContent)

FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG        v3.3.2
)

FetchContent_MakeAvailable(Catch2)

list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)
include(CTest)
include(Catch)

add_subdirectory(src/pydjinni/generator)
