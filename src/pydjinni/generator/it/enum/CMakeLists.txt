project(PyDjinniIntegrationTestEnum CXX)

define_test_case(EnumTest
    INTERFACE enum.djinni
    SOURCES
        src/helper.cpp
    OPTIONS
        generate.cpp.namespace=test::enum_test
)
