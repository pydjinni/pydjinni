#include "catch2/catch_test_macros.hpp"
#include "calculator.hpp"
#include "platform_interface.hpp"

TEST_CASE("Cpp.InterfaceTest") {
    GIVEN("a Calculator interface instance") {
        auto calculator = test::interface::Calculator::get_instance();
        WHEN("using the calculator interface") {
            auto result = calculator->add(40, 2);
            THEN("the C++ implementation of the calculator should have returned the correct sum") {
                REQUIRE(result == 42);
            }
        }
        THEN("the defined constant should be available") {
            REQUIRE(calculator->A == 5);
            REQUIRE(test::interface::Calculator::A == 5);
        }
        AND_GIVEN("an implementation for the PlatformInterface interface") {
            class PlatformInterfaceImpl : public test::interface::PlatformInterface {
                int8_t get_value() override { return 5; }
            };
            WHEN("passing using the implementation") {
                auto result = calculator->get_platform_value(std::make_shared<PlatformInterfaceImpl>());
                THEN("the expected result should be given") {
                    REQUIRE(result == 5);
                }
            }
        }
    }
}
