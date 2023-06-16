project(PyDjinniIntegrationTestRecord CXX)

define_test_case(RecordTest
    INTERFACE record.djinni
    SOURCES src/helper.cpp
    OPTIONS
        generate.cpp.namespace:test::record
)
