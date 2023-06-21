project(PyDjinniObjc_IntegrationTesting OBJC OBJCXX)

find_package(XCTest REQUIRED)

function(objc_test_case TEST_CASE_NAME)
    cmake_parse_arguments(TEST_CASE
            # options
            ""
            # one-value keywords
            ""
            # multi-value keywords
            "SOURCES;OPTIONS"
            # args
            ${ARGN}
            )
    set(TEST_LIBRARY_NAME ${TEST_CASE_NAME}Objc)
    set(TEST_BUNDLE_NAME ${TEST_LIBRARY_NAME}TestBundle)
    implement_test_case(${TEST_CASE_NAME} LANGUAGE objc
        OPTIONS
            ${TEST_CASE_OPTIONS}
            generate.objc.out.header:${CMAKE_CURRENT_LIST_DIR}/generated/include/objc
            generate.objc.out.source:${CMAKE_CURRENT_LIST_DIR}/generated/src/objc
            generate.objcpp.out.header:${CMAKE_CURRENT_LIST_DIR}/generated/include/objcpp
            generate.objcpp.out.source:${CMAKE_CURRENT_LIST_DIR}/generated/src/objcpp
        )

    add_library(${TEST_LIBRARY_NAME}
        ${objc_GENERATED_SOURCES}
        ${objcpp_GENERATED_SOURCES}
    )
    target_include_directories(${TEST_LIBRARY_NAME} PUBLIC ${objc_INCLUDE_DIR} ${objcpp_INCLUDE_DIR} ${objcpp_SOURCE_DIR})
    target_compile_options(${TEST_LIBRARY_NAME} PUBLIC "-fobjc-arc")
    target_link_libraries(${TEST_LIBRARY_NAME} PUBLIC test::${TEST_CASE_NAME} "-framework Foundation")
    xctest_add_bundle(${TEST_BUNDLE_NAME} ${TEST_LIBRARY_NAME} ${TEST_CASE_SOURCES})
    xctest_add_test(Objc.${TEST_CASE_NAME} ${TEST_BUNDLE_NAME})
endfunction()

add_subdirectory(enum)
add_subdirectory(flags)
add_subdirectory(record)
add_subdirectory(interface)