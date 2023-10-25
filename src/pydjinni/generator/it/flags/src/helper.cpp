// Copyright 2023 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "helper.hpp"
#include <cassert>

using namespace test::flags_test;

ExampleFlags Helper::get_flag(ExampleFlags example_flag) {
    assert(example_flag == ExampleFlags::A);
    return example_flag;
}

ExampleFlags Helper::get_all_flag(ExampleFlags example_flag) {
    assert(example_flag == ((ExampleFlags)0 | ExampleFlags::A | ExampleFlags::B)); // ExampleFlags::ALL
    return example_flag;
}

ExampleFlags Helper::get_none_flag(ExampleFlags example_flag) {
    assert(example_flag == (ExampleFlags)0); // ExampleFlags::NONE
    return example_flag;
}

