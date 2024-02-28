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
