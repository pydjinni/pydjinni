#include "catch2/catch_test_macros.hpp"
#include "example_enum.hpp"
#include "helper.hpp"

TEST_CASE("Cpp.EnumTest") {
    GIVEN("a ExampleEnum enum value") {
        auto enum_value = test::enum_test::ExampleEnum::A;
        WHEN("passing the enum through a helper interface") {
            auto new_enum_value = test::enum_test::Helper::get_enum(enum_value);
            THEN("the enum should still be the same") {
                REQUIRE(new_enum_value == test::enum_test::ExampleEnum::A);
            }
        }
    }
}
