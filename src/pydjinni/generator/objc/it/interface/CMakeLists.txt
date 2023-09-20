objc_test_case(InterfaceTest
    OPTIONS
        generate.objcpp.namespace=test::interface_test::objcpp
        generate.objc.strict_protocols=True
    SOURCES
        tests/InterfaceTests.m
)
