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

project(PyDjinniCppCli_SupportLib CXX CSharp)

add_library(cppcli_support_lib INTERFACE)
target_include_directories(cppcli_support_lib INTERFACE include)
target_link_libraries(cppcli_support_lib INTERFACE support_lib::cpp)
set_target_properties(cppcli_support_lib PROPERTIES FOLDER "support_lib")
add_library(support_lib::cppcli ALIAS cppcli_support_lib)
