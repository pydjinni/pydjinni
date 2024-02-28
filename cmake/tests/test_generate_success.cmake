# Copyright 2023 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

list(APPEND CMAKE_MODULE_PATH ../modules)
find_package(PyDjinni REQUIRED)
include(PyDjinni)
include(Testing)

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
assert(DEFINED cpp_GENERATED_HEADERS)
then("the variable cpp_INCLUDE_DIR should be set to the configured include dir")
assert(cpp_INCLUDE_DIR STREQUAL "out/cpp/header")
then("the variable java_GENERATED_SOURCES should be set")
assert(DEFINED java_GENERATED_SOURCES)
