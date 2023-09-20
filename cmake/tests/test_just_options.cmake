include(../modules/PyDjinni.cmake)
include(../modules/Testing.cmake)

scenario("Testing successful pydjinni execution with just custom options and no config file")

given("some required options")
list(APPEND OPTIONS generate.cpp.out=out/cpp)

given("a valid IDL file")

when("calling pydjinni_generate() for cpp with just the custom options and the config file being disabled")

pydjinni_generate(resources/valid_idl.djinni
    LANGUAGES cpp
    CONFIG None
    OPTIONS ${OPTIONS}
)

then("CMAKE_CONFIGURE_DEPENDS should contain just the input IDL file")
get_directory_property(DEPENDS CMAKE_CONFIGURE_DEPENDS)
assert_in_list("resources/valid_idl.djinni" DEPENDS)
list(LENGTH DEPENDS DEPENDS_LENGTH)
assert(DEPENDS_LENGTH EQUAL 1)

then("the variable cpp_GENERATED_HEADERS should be set")
assert(DEFINED cpp_GENERATED_HEADERS)
then("the variable cpp_GENERATED_SOURCES should be set")
assert(DEFINED cpp_GENERATED_SOURCES)
