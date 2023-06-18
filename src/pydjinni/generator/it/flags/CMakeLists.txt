project(PyDjinniIntegrationTestFlags CXX)

define_test_case(FlagsTest
    INTERFACE flags.djinni
    SOURCES
        src/helper.cpp
    OPTIONS
        generate.cpp.namespace:test::flags_test
)
