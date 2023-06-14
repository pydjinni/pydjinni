project(PyDjinniIntegrationTestRecord CXX)

define_test_case(RecordTest
    INTERFACE record.djinni
    SOURCES src/helper.cpp
    OPTIONS
        generate.cpp.out.header:generated/include/cpp
        generate.cpp.out.source:generated/src/cpp
        generate.cpp.namespace:test::record
)