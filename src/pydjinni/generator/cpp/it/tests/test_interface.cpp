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

#include "catch2/catch_test_macros.hpp"
#include "catch2/matchers/catch_matchers_exception.hpp"
#include "calculator.hpp"
#include "platform_interface.hpp"

TEST_CASE("Cpp.InterfaceTest") {
    GIVEN("a Calculator interface instance") {
        auto calculator = test::interface_test::Calculator::get_instance();
        WHEN("using the calculator interface") {
            auto result = calculator->add(40, 2);
            THEN("the C++ implementation of the calculator should have returned the correct sum") {
                REQUIRE(result == 42);
            }
        }
        AND_GIVEN("an implementation for the PlatformInterface interface") {
            class PlatformInterfaceImpl : public test::interface_test::PlatformInterface {
                int8_t get_value() override { return 5; }
            };
            WHEN("passing using the implementation") {
                auto result = calculator->get_platform_value(std::make_shared<PlatformInterfaceImpl>());
                THEN("the expected result should be given") {
                    REQUIRE(result == 5);
                }
            }
        }
        WHEN("calling a method that throws an exception") {
            THEN("the exception should be received") {
                REQUIRE_THROWS_MATCHES(calculator->throwing_exception(), std::runtime_error, Catch::Matchers::Message("shit hit the fan"));
            }
        }
    }
}
