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

#include "bar.hpp"
#include "helper.hpp"
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_exception.hpp>

TEST_CASE("FunctionTest") {
    WHEN("passing a lambda to the named_function method") {
        THEN("the internal assert should not be triggered") {
            test::function::Helper::named_function([](std::string input) -> bool {
                return input == "foo";
            });
        }
    }
    WHEN("passing a lambda to the named_function method") {
        THEN("the internal assert should not be triggered") {
            test::function::Helper::anonymous_function([](std::string input) -> bool {
                return input == "foo";
            });
        }
    }
    GIVEN("a (named) lambda returned by the helper") {
        const auto lambda = test::function::Helper::cpp_named_function();
        WHEN("calling the lambda with the correct value") {
            auto result = lambda("foo");
            THEN("true should be returned") {
                REQUIRE(result == true);
            }
        }
    }
    GIVEN("an (anonymous) lambda returned by the helper") {
        const auto lambda = test::function::Helper::cpp_anonymous_function();
        WHEN("calling the lambda with the correct value") {
            auto result = lambda("foo");
            THEN("true should be returned") {
                REQUIRE(result == true);
            }
        }
    }
    GIVEN("a function returned by the helper that throws an exception") {
        const auto lambda = test::function::Helper::cpp_function_throwing_exception();
        WHEN("calling the lambda") {
            THEN("an exception should be thrown") {
                REQUIRE_THROWS_MATCHES(lambda(), std::runtime_error, Catch::Matchers::Message("shit hit the fan"));
            }
        }
    }
    GIVEN("a function that throws a custom error type") {
        const auto lambda = test::function::Helper::cpp_function_throwing_bar_error();
        WHEN("using calling the function") {
            THEN("the exception should be thrown as expected") {
                REQUIRE_THROWS_MATCHES(
                    lambda(), test::function::Bar, Catch::Matchers::Message("this lambda has thrown an exception")
                );
            }
        }
    }
    WHEN("passing a lambda to the anonymous_function_passing_record method") {
        THEN("the internal assert should not be triggered") {
            test::function::Helper::anonymous_function_passing_record([](::test::function::Foo foo) -> bool {
                return foo.a == 32;
            });
        }
    }
    WHEN("passing a lambda that throws an exception") {
        THEN("the exception should be passed through correctly when the lambda is called inside") {
            REQUIRE_THROWS_MATCHES(
                test::function::Helper::function_parameter_throwing([]() -> void {
                    throw std::runtime_error("unexpected error from host");
                }),
                std::runtime_error,
                Catch::Matchers::Message("unexpected error from host")
            );
        }
    }
    WHEN("passing a nullptr instead of a lambda to an optional lambda parameter") {
        const auto result = test::function::Helper::optional_function_passing_null(nullptr);
        THEN("the result should be a nullptr") {
            REQUIRE(result == nullptr);
        }
    }
    WHEN("passing a lambda to an optional lambda parameter") {
        const auto result = test::function::Helper::optional_function_passing_function([](std::string input) {
            return input == "foo";
        });
        THEN("the resulting function should not be a nullptr") {
            REQUIRE(result != nullptr);
        }
        THEN("the function should be callable") {
            REQUIRE(result("foo") == true);
        }
    }
}
