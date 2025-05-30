# Copyright 2024 - 2025 jothepro
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

cmake_minimum_required(VERSION 3.24)

project(PyDjinniJava_SupportLib C CXX)

add_library(jni_support_lib
        include/pydjinni/jni/marshal.hpp
        include/pydjinni/jni/support.hpp
        src/pydjinni/support.cpp
)

target_include_directories(jni_support_lib PUBLIC include)
target_link_libraries(jni_support_lib PUBLIC support_lib::common JNI::JNI)
set_target_properties(jni_support_lib PROPERTIES FOLDER "support_lib")
add_library(support_lib::jni ALIAS jni_support_lib)
