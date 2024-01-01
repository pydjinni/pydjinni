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
#include "helper.hpp"
#include <sstream>

TEST_CASE("Cpp.RecordTest") {
    #ifdef _WIN32
    _putenv_s("TZ", "GMT");
    _tzset();
    #else
    std::string tz = "TZ=Etc/GMT-0";
    putenv(tz.data());
    tzset();
    #endif
    GIVEN("a PrimitiveTypes record instance") {
        const auto record = test::record::PrimitiveTypes(
                true, 8, 16, 32, 64, 32.32, 64.64,
                "test string",
                std::chrono::time_point<std::chrono::system_clock>(std::chrono::seconds(1688213309))
        );
        WHEN("passing the record through a helper interface") {
            const auto returned_record = test::record::Helper::get_primitive_types(record);
            THEN("the record should still contain the same data") {
                REQUIRE(returned_record.boolean_t == true);
                REQUIRE(returned_record.byte_t == 8);
                REQUIRE(returned_record.short_t == 16);
                REQUIRE(returned_record.int_t == 32);
                REQUIRE(returned_record.long_t == 64);
                REQUIRE(returned_record.float_t > 32);
                REQUIRE(returned_record.float_t < 33);
                REQUIRE(returned_record.double_t > 64);
                REQUIRE(returned_record.double_t < 65);
                REQUIRE(returned_record.string_t == "test string");
                REQUIRE(returned_record.date_t == std::chrono::time_point<std::chrono::system_clock>(std::chrono::seconds(1688213309)));
            }
            THEN("the records should pass the equality check") {
                REQUIRE(record == returned_record);
            }
        }
        WHEN("streaming the type to ostream") {
            std::stringstream ss;
            ss << record;
            const auto result = ss.str();
            THEN("a string representation of the type should be returned") {
                REQUIRE(result == "::test::record::PrimitiveTypes(boolean_t=1, byte_t=8, short_t=16, int_t=32, long_t=64, float_t=32.320000, double_t=64.640000, string_t=test string, date_t=2023-07-01T12:08:29+0000)");
            }
        }
    }
    GIVEN("A CollectionTypes record instance") {
        const auto record = test::record::CollectionTypes(
                {0, 1},
                {"foo", "bar"},
                {0, 1},
                {"foo", "bar"},
                {
                        {0, 1},
                },
                {
                        {"foo", "bar"}
                }
        );
        WHEN("passing the record through a helper interface") {
            const auto returned_record = test::record::Helper::get_collection_types(record);
            THEN("the record should still contain the same data") {
                REQUIRE(returned_record.int_list.size() == 2);
                REQUIRE(returned_record.int_list[0] == 0);
                REQUIRE(returned_record.int_list[1] == 1);

                REQUIRE(returned_record.string_list.size() == 2);
                REQUIRE(returned_record.string_list[0] == "foo");
                REQUIRE(returned_record.string_list[1] == "bar");

                REQUIRE(returned_record.int_set.size() == 2);
                REQUIRE(returned_record.int_set.contains(0));
                REQUIRE(returned_record.int_set.contains(1));

                REQUIRE(returned_record.string_set.size() == 2);
                REQUIRE(returned_record.string_set.contains("foo"));
                REQUIRE(returned_record.string_set.contains("bar"));

                REQUIRE(returned_record.int_int_map.size() == 1);
                REQUIRE(returned_record.int_int_map.at(0) == 1);

                REQUIRE(returned_record.string_string_map.size() == 1);
                REQUIRE(returned_record.string_string_map.at("foo") == "bar");
            }
        }
    }
    GIVEN("A OptionalTypes record instance") {
        const auto record = test::record::OptionalTypes(
                std::optional<int32_t>(42),
                std::optional<std::string>("optional")
        );
        WHEN("passing the record through a helper interface") {
            const auto returned_record = test::record::Helper::get_optional_types(record);
            THEN("the record should still contain the same data") {
                REQUIRE(returned_record.int_optional.has_value());
                REQUIRE(returned_record.int_optional.value() == 42);
                REQUIRE(returned_record.string_optional.has_value());
                REQUIRE(returned_record.string_optional.value() == "optional");
            }
        }
    }
    GIVEN("A BinaryTypes record instance") {
        const auto record = test::record::BinaryTypes(std::vector<uint8_t>{0x8F}, std::make_optional<std::vector<uint8_t>>({static_cast<uint8_t>(0x8F)}));
        WHEN("passing the record through a helper interface") {
            const auto returned_record = test::record::Helper::get_binary_types(record);
            THEN("the record should still contain the same data") {
                REQUIRE(returned_record.binary_t == std::vector<uint8_t>{0x8F});
                REQUIRE(returned_record.binary_optional.has_value());
                REQUIRE(returned_record.binary_optional.value() == std::vector<uint8_t>{0x8F});
            }
        }
    }
}
