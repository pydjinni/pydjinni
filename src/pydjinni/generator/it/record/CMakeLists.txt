project(PyDjinniIntegrationTestRecord CXX)

define_test_case(RecordTest
    INTERFACE record.pydjinni
    SOURCES
        src/helper.cpp
        include/base_record.hpp
    OPTIONS
        generate.cpp.namespace=test::record
)
target_include_directories(RecordTestBase PUBLIC include)
