#include "catch2/catch_test_macros.hpp"
#include "foo.hpp"
#include "helper.hpp"

TEST_CASE("Cpp.RecordTest") {
    GIVEN("a Foo record instance") {
        auto foo = test::record::Foo(true, 8, 16, 32, 64, 32.32, 64.64, "test string", {0, 1}, {"foo", "bar"}, std::optional<int32_t>(42), std::optional<std::string>("optional"));
        WHEN("passing the record through a helper interface") {
            auto new_foo = test::record::Helper::get_foo(foo);
            THEN("the record should still be the same") {
                REQUIRE(new_foo.boolean_t == true);
                REQUIRE(new_foo.byte_t == 8);
                REQUIRE(new_foo.short_t == 16);
                REQUIRE(new_foo.int_t == 32);
                REQUIRE(new_foo.long_t == 64);
                REQUIRE(new_foo.float_t > 32);
                REQUIRE(new_foo.float_t < 33);
                REQUIRE(new_foo.double_t > 64);
                REQUIRE(new_foo.double_t < 65);
                REQUIRE(new_foo.string_t == "test string");
                REQUIRE(new_foo.int_list.size() == 2);
                REQUIRE(new_foo.int_list[0] == 0);
                REQUIRE(new_foo.int_list[1] == 1);
                REQUIRE(new_foo.string_list.size() == 2);
                REQUIRE(new_foo.string_list[0] == "foo");
                REQUIRE(new_foo.string_list[1] == "bar");
                REQUIRE(new_foo.int_optional.has_value());
                REQUIRE(new_foo.int_optional.value() == 42);
                REQUIRE(new_foo.string_optional.has_value());
                REQUIRE(new_foo.string_optional.value() == "optional");
            }
        }
        THEN("the defined constant should be available") {
            REQUIRE(foo.BOOLEAN_C == true);
            REQUIRE(test::record::Foo::BOOLEAN_C == true);
            REQUIRE(foo.BYTE_C == 8);
            REQUIRE(test::record::Foo::BYTE_C == 8);
            REQUIRE(foo.SHORT_C == 16);
            REQUIRE(test::record::Foo::SHORT_C == 16);
            REQUIRE(foo.INT_C == 32);
            REQUIRE(test::record::Foo::INT_C ==32);
            REQUIRE(foo.LONG_C == 64);
            REQUIRE(test::record::Foo::LONG_C ==64);
            REQUIRE(foo.FLOAT_C > 32);
            REQUIRE(test::record::Foo::FLOAT_C > 32);
            REQUIRE(foo.FLOAT_C < 33);
            REQUIRE(test::record::Foo::FLOAT_C < 33);
            REQUIRE(foo.DOUBLE_C > 64);
            REQUIRE(test::record::Foo::DOUBLE_C < 65);
            REQUIRE(foo.DOUBLE_C < 65);
            REQUIRE(test::record::Foo::DOUBLE_C < 65);
        }
    }
}
