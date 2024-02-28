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
find_package(PyDjinni)
include(PyDjinni)
include(Testing)

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
