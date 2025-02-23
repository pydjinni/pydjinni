set(PROJECT_LANGUAGES CXX)
#> if "darwin" in platforms:
set(DARWIN_SYSTEM "Darwin;iOS")
if(CMAKE_SYSTEM_NAME IN_LIST DARWIN_SYSTEM)
  list(APPEND PROJECT_LANGUAGES OBJC OBJCXX)
endif()
#> endif
#> if "android" in platforms:
if(ANDROID)
    list(APPEND PROJECT_LANGUAGES C)
endif()
#> endif

project({{ target }} LANGUAGES ${PROJECT_LANGUAGES})

find_package(Microsoft.GSL REQUIRED)

pydjinni_generate(interface.pydjinni
    CONFIG ${CMAKE_SOURCE_DIR}/pydjinni.yaml
    LANGUAGES cpp java objc cppcli
    CLEAN
)

add_library(Cpp{{ target }} STATIC
    ${cpp_GENERATED_HEADERS}
    ${cpp_GENERATED_SOURCES}
        src/hello_world.cpp
)
add_library({{ target }}::Cpp ALIAS Cpp{{ target }})
target_include_directories(Cpp{{ target }} PUBLIC ${cpp_INCLUDE_DIR})
target_compile_features(Cpp{{ target }} PUBLIC cxx_std_23)
target_link_libraries(Cpp{{ target }} PUBLIC Microsoft.GSL::GSL)
set_target_properties(Cpp{{ target }} PROPERTIES
        CXX_STANDARD 23
        CXX_STANDARD_REQUIRED true
        CXX_EXTENSIONS false
        POSITION_INDEPENDENT_CODE TRUE
)

#> if "darwin" in platforms:
if(CMAKE_SYSTEM_NAME IN_LIST DARWIN_SYSTEM)
    add_library({{ target }} SHARED ${objc_GENERATED_SOURCES} ${objcpp_GENERATED_SOURCES} ${objc_GENERATED_HEADERS})
    target_include_directories({{ target }} PUBLIC ${objc_INCLUDE_DIR} PRIVATE ${objcpp_INCLUDE_DIR})
    set_target_properties({{ target }} PROPERTIES
        FRAMEWORK TRUE
        MACOSX_FRAMEWORK_IDENTIFIER {{ cpp_namespace | replace("::", ".") }}
        PUBLIC_HEADER "${objc_GENERATED_HEADERS}"
        XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER {{ cpp_namespace | replace("::", ".") }}
        XCODE_ATTRIBUTE_DEFINES_MODULE YES
        XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC YES
        XCODE_ATTRIBUTE_DEBUG_INFORMATION_FORMAT dwarf-with-dsym
        EXCLUDE_FROM_ALL TRUE
    )
    foreach(CONFIGURATION_TYPE ${CMAKE_CONFIGURATION_TYPES})
        string(TOUPPER ${CONFIGURATION_TYPE} CONFIGURATION_TYPE)
        set_target_properties({{ target }} PROPERTIES
            LIBRARY_OUTPUT_DIRECTORY_${CONFIGURATION_TYPE} .
        )
    endforeach()
    target_link_libraries({{ target }} PRIVATE {{ target }}::Cpp)
    install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/{{ target }}.framework.dSYM DESTINATION dist OPTIONAL)
    install(TARGETS {{ target }} DESTINATION dist)
endif()
#> endif
#> if "android" in platforms
if(ANDROID)
    find_package(Java 1.8 REQUIRED)
    include(UseJava)
    set(JAVA_AWT_LIBRARY NotNeeded)
    set(JAVA_AWT_INCLUDE_PATH NotNeeded)
    find_package(JNI REQUIRED)
    add_library({{ target }} SHARED ${jni_GENERATED_SOURCES})
    target_include_directories({{ target }} PRIVATE ${jni_INCLUDE_DIR})
    target_link_libraries({{ target }} PRIVATE JNI::JNI {{ target }}::Cpp)
    install(DIRECTORY ${java_SOURCE_DIR} DESTINATION dist/{{ target }})
    set_target_properties({{ target }} PROPERTIES EXCLUDE_FROM_ALL TRUE)
    install(TARGETS {{ target }} DESTINATION dist)
endif()
#> endif
#> if "windows" in platforms
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    add_library({{ target }} SHARED ${cppcli_GENERATED_SOURCES} ${cppcli_GENERATED_HEADERS})
    target_include_directories({{ target }} PUBLIC ${cppcli_INCLUDE_DIR})
    set_target_properties({{ target }} PROPERTIES
        COMMON_LANGUAGE_RUNTIME "netcore"
        DOTNET_TARGET_FRAMEWORK "net8.0"
        DOTNET_SDK "Microsoft.NET.Sdk"
        EXCLUDE_FROM_ALL TRUE
    )
    target_compile_options({{ target }} PRIVATE /doc)
    foreach(CONFIGURATION_TYPE ${CMAKE_CONFIGURATION_TYPES})
        string(TOUPPER ${CONFIGURATION_TYPE} CONFIGURATION_TYPE)
        set_target_properties({{ target }} PROPERTIES
            PDB_OUTPUT_DIRECTORY_${CONFIGURATION_TYPE} ${CMAKE_BINARY_DIR}/dist
            LIBRARY_OUTPUT_DIRECTORY_${CONFIGURATION_TYPE} ${CMAKE_BINARY_DIR}/dist
            RUNTIME_OUTPUT_DIRECTORY_${CONFIGURATION_TYPE} ${CMAKE_BINARY_DIR}/dist
        )
    endforeach()
    target_link_libraries({{ target }} PRIVATE {{ target }}::Cpp)
    install(TARGETS {{ target }} DESTINATION dist)
endif()
#> endif
