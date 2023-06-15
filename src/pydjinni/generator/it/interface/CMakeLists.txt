project(PyDjinniIntegrationTestInterface CXX)

define_test_case(InterfaceTest
    INTERFACE interface.djinni
    SOURCES
        src/calculator.cpp
        src/calculator_impl.cpp
        src/calculator_impl.hpp
    OPTIONS
        generate.cpp.out.header:generated/include/cpp
        generate.cpp.out.source:generated/src/cpp
        generate.cpp.namespace:test::interface
)