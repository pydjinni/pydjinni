include(../modules/PyDjinni.cmake)
include(../modules/Testing.cmake)

scenario("Testing error in pydjinni execution because of an invalid IDL file")

given("an invalid IDL file and a valid config file")
set(IDL_FILE resources/invalid_idl.djinni)
set(CONFIG_FILE resources/valid_config.yaml)

when("calling pydjinni_generate() for cpp")
then("the execution should fail")
pydjinni_generate(${IDL_FILE}
    LANGUAGES cpp
    CONFIG ${CONFIG_FILE}
)
