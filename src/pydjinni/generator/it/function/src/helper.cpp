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
#include <stdexcept>

using namespace test::function;

void Helper::named_function(const std::function<bool(int32_t)>& callback) {
    assert(callback(42));
}

void Helper::anonymous_function(const std::function<bool(int32_t)>& callback) {
    assert(callback(42));
}

std::function<bool(int32_t)> Helper::cpp_named_function() {
    return [](int32_t input){
        return input == 42;
    };
}

std::function<bool(int32_t)> Helper::cpp_anonymous_function() {
    return [](int32_t input){
        return input == 42;
    };
}

std::function<void()> Helper::cpp_function_throwing_exception() {
    return [](){
        throw std::runtime_error("shit hit the fan");
    };
}
