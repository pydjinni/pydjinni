#include <catch2/catch_test_macros.hpp>

SCENARIO("this is a test test") {
    GIVEN("a test") {
        WHEN("testing") {
            THEN("foo") {
                REQUIRE("foo" == "foo");
            }
        }
    }
}
