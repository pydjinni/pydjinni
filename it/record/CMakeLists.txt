set(PROJECT_LANGUAGES CXX)
if(PYDJINNI_OBJC)
  list(APPEND PROJECT_LANGUAGES OBJC OBJCXX)
endif()
if(PYDJINNI_JNI)
    list(APPEND PROJECT_LANGUAGES C)
endif()


project(PyDjinniIntegrationTestRecord LANGUAGES ${PROJECT_LANGUAGES})

pydjinni_generate(record.djinni CLEAN LANGUAGES cpp java objc )

add_library(RecordTest STATIC
    ${cpp_GENERATED_SOURCES}
    cpp/helper.cpp
)
target_include_directories(RecordTest PUBLIC ${cpp_INCLUDE_DIR})
target_compile_features(RecordTest PUBLIC cxx_std_20)
add_library(test::record ALIAS RecordTest)

if(PYDJINNI_JNI)
    add_library(RecordTestJni SHARED
        ${jni_GENERATED_SOURCES}
    )
    target_include_directories(RecordTestJni PUBLIC ${jni_INCLUDE_DIR} ${jni_SOURCE_DIR})
    target_link_libraries(RecordTestJni PUBLIC JNI::JNI test::record)
    add_library(test::record::jni ALIAS RecordTestJni)

    add_jar(RecordTestJava
        SOURCES
            ${java_GENERATED_SOURCES}
            java/TestRecord.java
        INCLUDE_JARS
            ${junit-jupiter-api_JAR}
            ${apiguardian-api_JAR}
            ${junit-platform-commons_JAR}
    )
    add_dependencies(RecordTestJni RecordTestJava)
endif()

if(PYDJINNI_OBJC)
    add_executable(RecordTestObjc ${objc_GENERATED_SOURCES} ${objcpp_GENERATED_SOURCES})
    target_include_directories(RecordTestObjc PUBLIC ${objc_INCLUDE_DIR} ${objcpp_INCLUDE_DIR} ${objcpp_SOURCE_DIR})
    target_compile_options(RecordTestObjc PUBLIC "-fobjc-arc")
    target_link_libraries(RecordTestObjc PUBLIC test::record)
endif()
