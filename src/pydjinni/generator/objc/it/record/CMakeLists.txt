objc_test_case(RecordTest
    OPTIONS
        generate.objcpp.namespace=test::record_test::objcpp
    SOURCES
        tests/PrimitiveTypesTests.m
        tests/CollectionTypesTests.m
        tests/OptionalTypesTests.m
        tests/BinaryTypesTests.m
        tests/BaseRecordTests.m
)
target_sources(RecordTestObjc
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include/BaseRecord.h
        ${CMAKE_CURRENT_SOURCE_DIR}/src/BaseRecord.m
)
target_include_directories(RecordTestObjc PUBLIC include)
