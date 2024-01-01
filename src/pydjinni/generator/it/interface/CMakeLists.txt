project(PyDjinniIntegrationTestInterface CXX)

define_test_case(InterfaceTest
    INTERFACE interface.djinni
    SOURCES
        src/calculator.cpp
        src/calculator_impl.cpp
        src/calculator_impl.hpp
        src/deprecation_test.cpp
    OPTIONS
        generate.cpp.namespace=test::interface
)
