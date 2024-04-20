cmake_minimum_required(VERSION 3.24)

project({{ target }})

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/modules)
find_package(PyDjinni)
include(PyDjinni)

add_subdirectory(lib)
