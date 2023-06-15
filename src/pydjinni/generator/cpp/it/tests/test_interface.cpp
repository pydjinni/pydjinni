#include "catch2/catch_test_macros.hpp"
#include "calculator.hpp"

SCENARIO("Testing the generated interface") {
    GIVEN("a Calculator interface instance") {
        auto calculator = test::interface::Calculator::get_instance();
        WHEN("using the calculator interface") {
            auto result = calculator->add(40, 2);
            THEN("the C++ implementation of the calculator should have returned the correct sum") {
                REQUIRE(result == 42);
            }
        }
    }
}
