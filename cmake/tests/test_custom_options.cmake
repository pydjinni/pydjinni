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

scenario("Testing successful pydjinni execution with custom options")

given("Valid IDL and config files")
set(CONFIG_FILE resources/valid_config.yaml)
set(IDL_FILE resources/valid_idl.djinni)
given("a custom option to change the out directory of the generated java code")
set(OPTION generate.java.out=out/java-custom)

when("calling pydjinni_generate with the custom option")

pydjinni_generate(${IDL_FILE}
    LANGUAGES java
    CONFIG ${CONFIG_FILE}
    OPTIONS
        ${OPTION}
)

then("the custom options should be taken into account in the generated output")

assert(DEFINED java_GENERATED_SOURCES)
assert_in_list("out/java-custom/foo/bar/Foo.java" java_GENERATED_SOURCES)
