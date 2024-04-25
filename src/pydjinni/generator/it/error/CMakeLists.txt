project(PyDjinniIntegrationTestRecord CXX)

define_test_case(ErrorTest
    INTERFACE error.pydjinni
    SOURCES
        src/helper.cpp
    OPTIONS
        generate.cpp.namespace=test::error
)
