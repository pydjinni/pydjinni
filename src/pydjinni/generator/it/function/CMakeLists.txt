project(PyDjinniIntegrationTestFunction CXX)

define_test_case(FunctionTest
    INTERFACE function.djinni
    SOURCES src/helper.cpp
    OPTIONS
        generate.cpp.namespace:test::function
)
