objc_test_case(FunctionTest
    OPTIONS
        generate.objcpp.namespace:test::function_test::objcpp
        generate.objc.strict_protocols:True
    SOURCES
        tests/FunctionTests.m
)
