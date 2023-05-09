project(PyDjinniIntegrationTestRecord C CXX)

pydjinni_generate(record.djinni CLEAN LANGUAGES cpp java objc )

add_library(record_test STATIC
    ${cpp_GENERATED_SOURCES}
    cpp/helper.cpp
)

target_include_directories(record_test PUBLIC generated/cpp)

target_link_libraries(record_test PUBLIC support_lib::common)

add_jar(RecordTest
    SOURCES
        ${java_GENERATED_SOURCES}
        java/TestRecord.java
    INCLUDE_JARS
        ${junit-jupiter-api_JAR}
        ${apiguardian-api_JAR}
        ${junit-platform-commons_JAR}
)
