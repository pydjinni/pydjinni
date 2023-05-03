include(../modules/PyDjinni.cmake)
include(../modules/Testing.cmake)

scenario("Testing the case that no config file is provided")

given("Just a valid IDL file")
set(IDL_FILE resources/valid_idl.djinni)

when("calling pydjinni_generate without providing a config file")
then("generation should fail because no default 'pydjinni.yaml' can be found")
pydjinni_generate(${IDL_FILE}
    LANGUAGES cpp
)
