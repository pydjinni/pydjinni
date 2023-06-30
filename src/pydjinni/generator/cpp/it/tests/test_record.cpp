#include "catch2/catch_test_macros.hpp"
#include "constant_types.hpp"
#include "helper.hpp"

TEST_CASE("Cpp.RecordTest") {
    GIVEN("a PrimitiveTypes record instance") {
        const auto record = test::record::PrimitiveTypes(
                true, 8, 16, 32, 64, 32.32, 64.64,
                "test string"
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
    GIVEN("A ConstantTypes record instance") {
        const auto record = test::record::ConstantTypes();
        THEN("the defined constants should be available via the class instance") {
            REQUIRE(record.BOOLEAN_C == true);
            REQUIRE(record.BYTE_C == 8);
            REQUIRE(record.SHORT_C == 16);
            REQUIRE(record.INT_C == 32);
            REQUIRE(record.LONG_C == 64);
            REQUIRE(record.FLOAT_C > 32);
            REQUIRE(record.FLOAT_C < 33);
            REQUIRE(record.DOUBLE_C > 64);
            REQUIRE(record.DOUBLE_C < 65);

        }
        THEN("the defined constants should be available via the class type") {
            REQUIRE(test::record::ConstantTypes::BOOLEAN_C == true);
            REQUIRE(test::record::ConstantTypes::BYTE_C == 8);
            REQUIRE(test::record::ConstantTypes::SHORT_C == 16);
            REQUIRE(test::record::ConstantTypes::INT_C ==32);
            REQUIRE(test::record::ConstantTypes::LONG_C ==64);
            REQUIRE(test::record::ConstantTypes::FLOAT_C > 32);
            REQUIRE(test::record::ConstantTypes::FLOAT_C < 33);
            REQUIRE(test::record::ConstantTypes::DOUBLE_C < 65);
            REQUIRE(test::record::ConstantTypes::DOUBLE_C < 65);
        }
    }
}
