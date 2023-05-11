include(../modules/PyDjinni.cmake)
include(../modules/Testing.cmake)

scenario("Testing successful pydjinni execution with custom options")

given("Valid IDL and config files")
set(CONFIG_FILE resources/valid_config.yaml)
set(IDL_FILE resources/valid_idl.djinni)
given("a custom option to change the out directory of the generated java code")
set(OPTION generate.java.out:out/java-custom)

when("calling pydjinni_generate with the custom option")

pydjinni_generate(${IDL_FILE}
    LANGUAGES java
    CONFIG ${CONFIG_FILE}
    OPTIONS
        ${OPTION}
)

then("the custom options should be taken into account in the generated output")

assert(java_GENERATED_SOURCES)
assert_in_list("out/java-custom/foo/bar/Foo.java" java_GENERATED_SOURCES)
