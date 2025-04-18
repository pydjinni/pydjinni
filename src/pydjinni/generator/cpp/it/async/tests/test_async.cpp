// Copyright 2023 - 2025 jothepro
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

#include "asynchronous.hpp"
#include "test/async.hpp"
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_exception.hpp>

class MultiplyCallbackImpl: public ::test::async_test::MultiplyCallback {
    pydjinni::coroutine::task<int32_t> invoke(int32_t a, int32_t b) noexcept override {
        co_return a* b;
    }
};

struct NoParametersNoReturnImpl: public ::test::async_test::NoParametersNoReturnCallback {
    bool callbackInvoked = false;
    pydjinni::coroutine::task<> invoke() noexcept override {
        callbackInvoked = true;
        co_return;
    }
};

class ThrowingCallbackImpl: public ::test::async_test::ThrowingCallback {
    pydjinni::coroutine::task<> invoke() override {
        throw std::runtime_error("throwing from callback");
        co_return;
    }
};

TEST_CASE("AsyncTest") {
    ASYNC {
        GIVEN("an Asynchronous object instance") {
            auto instance = co_await test::async_test::Asynchronous::get_instance();
            WHEN("awaiting the `add` method") {
                auto result = co_await instance->add(40, 2);
                THEN("The correct result should be returned") {
                    REQUIRE(result == 42);
                }
            }
            WHEN("awaiting the `no_parameters_no_return` method") {
                co_await instance->no_parameters_no_return();
                THEN("it should finish successfully") {
                    SUCCEED();
                }
            }
            WHEN("awaiting the `throwing_exception` method") {
                THEN("the exception should be received") {
                    REQUIRE_THROWS_MATCHES(
                        co_await instance->throwing_exception(),
                        std::runtime_error,
                        Catch::Matchers::Message("asynchronous runtime error")
                    );
                }
            }
            WHEN("awaiting the `multiply_callback` method and passing a callback implementation") {
                auto result = co_await instance->multiply_callback(std::make_shared<MultiplyCallbackImpl>());
                THEN("the correct result should be returned") {
                    REQUIRE(result == 42);
                }
            }
            WHEN("awaiting the `no_parameters_no_return_callback` method and passing a callback implementation") {
                auto callback = std::make_shared<NoParametersNoReturnImpl>();
                co_await instance->no_parameters_no_return_callback(callback);
                THEN("it should finish successfully") {
                    REQUIRE(callback->callbackInvoked);
                }
            }
            WHEN("awaiting the `throwing_callback` method and passing a callback implementation") {
                THEN("the exception should be received") {
                    REQUIRE_THROWS_MATCHES(
                        co_await instance->throwing_callback(std::make_shared<ThrowingCallbackImpl>()),
                        std::runtime_error,
                        Catch::Matchers::Message("throwing from callback")
                    );
                }
            }
        }
    }
    RUN_SYNCHRONOUS
}
