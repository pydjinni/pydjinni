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

#include "calculator_impl.hpp"
#include <cassert>
#include <stdexcept>
#include <string>

using namespace test::interface_test;

int8_t CalculatorImpl::add(int8_t a, int8_t b) noexcept {
    return a + b;
}

int8_t CalculatorImpl::get_platform_value(const std::shared_ptr<PlatformInterface>& platform) noexcept {
    auto val =  platform->get_value();
    assert(val == 5);
    return val;
}

void CalculatorImpl::no_parameters_no_return() noexcept {}

void CalculatorImpl::throwing_exception() {
    throw std::runtime_error("shit hit the fan");
}

void CalculatorImpl::no_parameters_no_return_callback(const std::shared_ptr<NoParametersNoReturnCallback> &callback) noexcept {
    callback->invoke();
}

void CalculatorImpl::throwing_callback(const std::shared_ptr<ThrowingCallback> &callback) {
    try {
        callback->invoke();
    } catch (const std::exception& e) {
        assert(std::string("exception from callback") == e.what());
        std::rethrow_exception(std::current_exception());
    }
    assert(false); // this should never be reached because of the exception
}
