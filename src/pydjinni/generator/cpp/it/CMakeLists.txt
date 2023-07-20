project(PyDjinniCpp_IntegrationTesting CXX)

function(cpp_test_case TEST_CASE_NAME)

    cmake_parse_arguments(TEST_CASE
            # options
            ""
            # one-value keywords
            ""
            # multi-value keywords
            "SOURCES"
            # args
            ${ARGN}
            )
    add_executable(${TEST_CASE_NAME}Cpp
        ${TEST_CASE_SOURCES}
    )

    target_link_libraries(${TEST_CASE_NAME}Cpp
        PRIVATE
            Catch2::Catch2WithMain
            test::${TEST_CASE_NAME}
    )

catch_discover_tests(${TEST_CASE_NAME}Cpp)

endfunction()

cpp_test_case(RecordTest
    SOURCES
        tests/test_record.cpp
)

cpp_test_case(InterfaceTest
    SOURCES
        tests/test_interface.cpp
)

cpp_test_case(EnumTest
    SOURCES
        tests/test_enum.cpp
)

cpp_test_case(FlagsTest
    SOURCES
        tests/test_flags.cpp
)

cpp_test_case(FunctionTest
    SOURCES
        tests/test_function.cpp
)