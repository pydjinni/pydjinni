#include "catch2/catch_test_macros.hpp"
#include "example_flags.hpp"
#include "helper.hpp"

SCENARIO("Testing the generated flags") {
    GIVEN("a ExampleFlags flag value") {
        auto flag_value = test::flags_test::ExampleFlags::A;
        WHEN("passing the flag through a helper interface") {
            auto new_enum_value = test::flags_test::Helper::get_flag(flag_value);
            THEN("the flag should still be the same") {
                REQUIRE(new_enum_value == test::flags_test::ExampleFlags::A);
            }
        }
    }
    GIVEN("a ExampleFlags 'all' flag value") {
        auto flag_value = test::flags_test::ExampleFlags::ALL;
        WHEN("passing the flag through a helper interface") {
            auto new_enum_value = test::flags_test::Helper::get_all_flag(flag_value);
            THEN("the flag should still be the same") {
                REQUIRE(new_enum_value == test::flags_test::ExampleFlags::ALL);
            }
        }
    }
    GIVEN("a ExampleFlags 'none' flag value") {
        auto flag_value = test::flags_test::ExampleFlags::NONE;
        WHEN("passing the flag through a helper interface") {
            auto new_enum_value = test::flags_test::Helper::get_none_flag(flag_value);
            THEN("the flag should still be the same") {
                REQUIRE(new_enum_value == test::flags_test::ExampleFlags::NONE);
            }
        }
    }
}
