include(../modules/PyDjinni.cmake)
include(../modules/Testing.cmake)

scenario("Testing changed working directory")

given("a custom working directory")
set(WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/resources)
given("a valid IDL and config file")
set(IDL_FILE valid_idl.djinni)
set(CONFIG_FILE valid_config.yaml)

when("calling pydjinni_generate() with the custom working directory")
then("generation should succeed")
pydjinni_generate(${IDL_FILE}
    LANGUAGES cpp java objc
    CONFIG ${CONFIG_FILE}
    WORKING_DIRECTORY ${WORKING_DIRECTORY}
)
