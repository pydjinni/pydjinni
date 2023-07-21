#include "catch2/catch_test_macros.hpp"
#include "catch2/matchers/catch_matchers_exception.hpp"
#include "helper.hpp"

TEST_CASE("Cpp.FunctionTest") {
    WHEN("passing a lambda to the named_function method") {
        THEN("the internal asser should not be triggered") {
            test::function::Helper::named_function([](int32_t input) -> bool {
                return input == 42;
            });
        }
    }
    WHEN("passing a lambda to the named_function method") {
        THEN("the internal asser should not be triggered") {
            test::function::Helper::anonymous_function([](int32_t input) -> bool {
                return input == 42;
            });
        }
    }
    GIVEN("a (named) lambda returned by the helper") {
        auto lambda = test::function::Helper::cpp_named_function();
        WHEN("calling the lambda with the correct value") {
            auto result = lambda(42);
            THEN("true should be returned") {
                REQUIRE(result == true);
            }
        }
    }
    GIVEN("an (anonymous) lambda returned by the helper") {
        auto lambda = test::function::Helper::cpp_anonymous_function();
        WHEN("calling the lambda with the correct value") {
            auto result = lambda(42);
            THEN("true should be returned") {
                REQUIRE(result == true);
            }
        }
    }
    GIVEN("a function returned by the helper that throws an excption") {
        auto lambda = test::function::Helper::cpp_function_throwing_exception();
        WHEN("calling the lambda") {
            THEN("an exception should be thrown") {
                REQUIRE_THROWS_MATCHES(lambda(), std::runtime_error, Catch::Matchers::Message("shit hit the fan"));
            }
        }
    }
}
