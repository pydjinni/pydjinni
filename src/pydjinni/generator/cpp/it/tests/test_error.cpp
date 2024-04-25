// Copyright 2024 jothepro
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

#include "catch2/catch_test_macros.hpp"
#include "test/async.hpp"
#include "helper.hpp"
#include "foo_error.hpp"
#include "catch2/matchers/catch_matchers_exception.hpp"

TEST_CASE("Cpp.ErrorTest") {
    WHEN("calling an interface that throws an error") {
        THEN("the expected exception should be thrown") {
            REQUIRE_THROWS_MATCHES(
                    ::test::error::Helper::throwing_error(),
                    ::test::error::FooError::SomethingWrong,
                    Catch::Matchers::Message("some error")
            );
        }
    }
    WHEN("calling an interface that throws an error with parameters") {
        THEN("the expected exception should be thrown") {
            REQUIRE_THROWS_MATCHES(
                    ::test::error::Helper::throwing_with_parameters(),
                    ::test::error::FooError::SomethingWithParameters,
                    Catch::Matchers::Message("some error message")
            );
        }
        THEN("the expected parameters should be set on the exception") {
            try {
                ::test::error::Helper::throwing_with_parameters();
            } catch (const ::test::error::FooError::SomethingWithParameters& e) {
                REQUIRE(e.parameter == 42);
            }
        }
    }
    ASYNC {
        WHEN("calling a coroutine that throws an error") {
            THEN("the expected exception should be thrown") {
                REQUIRE_THROWS_MATCHES(
                    co_await ::test::error::Helper::throwing_async(),
                    ::test::error::FooError::SomethingWrong,
                    Catch::Matchers::Message("something wrong in coroutine")
                );
            }
        }
        WHEN("using a coroutine callback interface that throws an error") {
            struct AsyncThrowingCallbackImpl : public ::test::error::AsyncThrowingCallback {
                bool callback_called = false;

                ::pydjinni::coroutine::task<> throwing_error() override {
                    callback_called = true;
                    throw ::test::error::FooError::SomethingWrong("some async callback error");
                    co_return;
                }
            };
            auto callback = std::make_shared<AsyncThrowingCallbackImpl>();
            THEN("the exception thrown by the callback should be forwarded to the calling coroutine accordingly") {
                REQUIRE_THROWS_MATCHES(
                    co_await ::test::error::Helper::throwing_async_callback_error(callback),
                    ::test::error::FooError::SomethingWrong,
                    Catch::Matchers::Message("some async callback error")
                );

            }
        }
    } RUN_SYNCHRONOUS
}
