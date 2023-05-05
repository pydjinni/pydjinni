#include <catch2/catch_test_macros.hpp>

SCENARIO("second test") {
    GIVEN("a test2") {
        WHEN("testing2") {
            THEN("foo2") {
                REQUIRE(true);
            }
        }
    }
}
