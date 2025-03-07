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

void Helper::named_function(const std::function<bool(std::string)>& callback) noexcept {
    assert(callback("foo"));
}

void Helper::anonymous_function(const std::function<bool(std::string)>& callback) noexcept {
    assert(callback("foo"));
}

std::function<bool(std::string)> Helper::cpp_named_function() noexcept {
    return [](std::string input) noexcept -> bool {
        return input == "foo";
    };
}

std::function<bool(std::string)> Helper::cpp_anonymous_function() noexcept {
    return [](std::string input) noexcept -> bool {
        return input == "foo";
    };
}

std::function<void()> Helper::cpp_function_throwing_exception() noexcept {
    return []() -> void {
        throw std::runtime_error("shit hit the fan");
    };
}

std::function<void()> Helper::cpp_function_throwing_bar_error() noexcept {
    return []() -> void {
        throw Bar::BadStuff("this lambda has thrown an exception");
    };
}

void Helper::anonymous_function_passing_record(const std::function<bool(::test::function::Foo foo)>& callback) noexcept {
    assert(callback(Foo(32)));
}

void Helper::function_parameter_throwing(const std::function<void()>& callback) {
    try {
        callback();
    } catch (const std::exception& e) {
        assert(std::string("unexpected error from host") == e.what());
        std::rethrow_exception(std::current_exception());
    }
    assert(false); // this should never be reached because of the exception
}

std::function<bool(std::string)> Helper::optional_function_passing_null(const std::function<bool(std::string)> & param) noexcept {
    assert(param == nullptr);
    return param;
}

std::function<bool(std::string)> Helper::optional_function_passing_function(const std::function<bool(std::string)> & param) noexcept {
    assert(param != nullptr);
    assert(param("foo"));
    return param;
}
