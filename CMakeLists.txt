cmake_minimum_required(VERSION 3.6.0)

project(PyDjinniSupportLib C CXX)

option(BUILD_TESTING "Whether testing should be enabled or not" ON)

set(PYDJINNI_LANGUAGE_TARGETS_DEFAULT cpp)
if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    list(APPEND PYDJINNI_LANGUAGE_TARGETS_DEFAULT objc java)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    list(APPEND PYDJINNI_LANGUAGE_TARGETS_DEFAULT java)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    list(APPEND PYDJINNI_LANGUAGE_TARGETS_DEFAULT java)
endif()

set(PYDJINNI_LANGUAGE_TARGETS ${PYDJINNI_LANGUAGE_TARGETS_DEFAULT} CACHE STRING "List of languages that should be targeted" )

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")
Include(FetchContent)
Include(PyDjinni)

if(BUILD_TESTING)
    Include(IntegrationTesting)
    enable_testing()
    FetchContent_Declare(
      Catch2
      GIT_REPOSITORY https://github.com/catchorg/Catch2.git
      GIT_TAG        v3.3.2
    )
    FetchContent_MakeAvailable(Catch2)
    include(Catch)
endif()

add_subdirectory(src/pydjinni/generator)
