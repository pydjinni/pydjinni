
define_property(TARGET
        PROPERTY PYDJINNI_INTERFACE
        BRIEF_DOCS "The pydjinni IDL file that was used when generating the targets interface")
define_property(TARGET
        PROPERTY PYDJINNI_OPTIONS
        BRIEF_DOCS "The pydjinni options that where applied when generating the targets interface")

function(define_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
        # options
        ""
        # one-value keywords
        "INTERFACE"
        # multi-value keywords
        "OPTIONS;SOURCES"
        # args
        ${ARGN}
        )

    list(APPEND TEST_CASE_OPTIONS
        generate.cpp.out.header:generated/include/cpp
        generate.cpp.out.source:generated/src/cpp
    )

    pydjinni_generate(${TEST_CASE_INTERFACE} CLEAN
        LANGUAGES cpp
        CONFIG None
        OPTIONS
            ${TEST_CASE_OPTIONS}
    )
    set(BASE_LIB_NAME ${TEST_CASE_NAME}Base)
    add_library(${BASE_LIB_NAME} STATIC
            ${cpp_GENERATED_HEADERS}
            ${TEST_CASE_SOURCES}
    )
    target_include_directories(${BASE_LIB_NAME} PUBLIC ${cpp_INCLUDE_DIR})
    target_compile_features(${BASE_LIB_NAME} PUBLIC cxx_std_20)
    add_library(test::${TEST_CASE_NAME} ALIAS ${BASE_LIB_NAME})
    set_target_properties(${BASE_LIB_NAME}
        PROPERTIES
            PYDJINNI_INTERFACE "${TEST_CASE_INTERFACE}"
            PYDJINNI_OPTIONS "${TEST_CASE_OPTIONS}"
            POSITION_INDEPENDENT_CODE ON
    )

endfunction()

macro(implement_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
        # options
        ""
        # one-value keywords
        "LANGUAGE"
        # multi-value keywords
        "OPTIONS"
        # args
        ${ARGN}
    )
    get_target_property(TEST_CASE_INTERFACE test::${TEST_CASE_NAME} PYDJINNI_INTERFACE)
    get_target_property(TEST_CASE_PARENT_OPTIONS test::${TEST_CASE_NAME} PYDJINNI_OPTIONS)
    get_target_property(TEST_CASE_WORKING_DIRECTORY test::${TEST_CASE_NAME} SOURCE_DIR)
    pydjinni_generate(${TEST_CASE_INTERFACE} CLEAN
        LANGUAGES ${TEST_CASE_LANGUAGE}
        CONFIG None
        OPTIONS ${TEST_CASE_PARENT_OPTIONS} ${TEST_CASE_OPTIONS}
        WORKING_DIRECTORY ${TEST_CASE_WORKING_DIRECTORY}
    )
endmacro()
