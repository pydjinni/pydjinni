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

#include "catch2/catch_test_macros.hpp"
#include "example_flags.hpp"
#include "helper.hpp"

TEST_CASE("FlagsTest") {
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
    GIVEN("a ExampleFlags flag value with no options set") {
        auto flag_value = test::flags_test::ExampleFlags::NONE;
        WHEN("stringifying the flag") {
            auto result = std::format("{}", flag_value);
            THEN("the stringified vaue should be ''") {
                REQUIRE(result.empty());
            }
        }
    }
    GIVEN("a ExampleFlags flag value with only the 'B' option set") {
        auto flag_value = test::flags_test::ExampleFlags::B;
        WHEN("stringifying the flag") {
            auto result = std::format("{}", flag_value);
            THEN("the stringified vaue should be 'B'") {
                REQUIRE(result == "B");
            }
        }
    }
    GIVEN("a ExampleFlags flag value with multiple options set") {
        auto flag_value = test::flags_test::ExampleFlags::A | test::flags_test::ExampleFlags::B;
        WHEN("stringifying the flag") {
            auto result = std::format("{}", flag_value);
            THEN("the stringified vaue should be 'A | B'") {
                REQUIRE(result == "A | B");
            }
        }
    }
}
