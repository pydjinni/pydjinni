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

cmake_minimum_required(VERSION 3.10)

project(PyDjinniObjc_SupportLib OBJC OBJCXX)

add_library(objc_support_lib
        include/pydjinni/coroutine/schedule.h
        src/support.mm
        src/pydjinni/support.mm
        src/pydjinni/error.mm
        src/pydjinni/proxy_cache.mm
)

target_compile_options(objc_support_lib PUBLIC "-fobjc-arc")
target_include_directories(objc_support_lib PUBLIC include)
target_link_libraries(objc_support_lib PUBLIC support_lib::cpp)
set_target_properties(objc_support_lib PROPERTIES FOLDER "support_lib")
add_library(support_lib::objc ALIAS objc_support_lib)
