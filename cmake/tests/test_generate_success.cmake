include(../modules/PyDjinni.cmake)
include(../modules/Testing.cmake)

scenario("Testing successful pydjinni execution")

given("Valid IDL and config files")
set(CONFIG_FILE resources/valid_config.yaml)
set(IDL_FILE resources/valid_idl.djinni)

when("calling pydjinni_generate() for cpp, java and objc")
pydjinni_generate(${IDL_FILE}
    LANGUAGES cpp java objc
    CONFIG ${CONFIG_FILE}
)

then("CMAKE_CONFIGURE_DEPENDS should contain both the IDL and config file")
get_directory_property(DEPENDS CMAKE_CONFIGURE_DEPENDS)
assert_in_list("resources/valid_idl.djinni" DEPENDS)
assert_in_list("resources/valid_config.yaml" DEPENDS)
list(LENGTH DEPENDS DEPENDS_LENGTH)
assert(DEPENDS_LENGTH EQUAL 2)

then("the variable cpp_GENERATED_HEADERS should be set")
assert(cpp_GENERATED_HEADERS)
then("the variable cpp_INCLUDE_DIR should be set to the configured include dir")
assert(cpp_INCLUDE_DIR STREQUAL "out/cpp/header")
then("the variable cpp_SOURCE_DIR should be set to the configured source dir")
assert(cpp_SOURCE_DIR STREQUAL "out/cpp/source")
then("the variable cpp_GENERATED_SOURCES should be set")
assert(cpp_GENERATED_SOURCES)
then("the variable java_GENERATED_SOURCES should be set")
assert(java_GENERATED_SOURCES)
