# Copyright 2025 jothepro
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

kotlin_test_case(FlagsTest
    OPTIONS
        generate.java.package=test.flags_test
        generate.jni.identifier.file.prefix=marshal_
        generate.jni.identifier.file.style=snake_case
        generate.jni.namespace=test::flags::jni
    SOURCES
        tests/FlagsTest.kt
)
