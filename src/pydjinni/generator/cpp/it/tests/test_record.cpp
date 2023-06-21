#include "catch2/catch_test_macros.hpp"
#include "foo.hpp"
#include "helper.hpp"

TEST_CASE("Cpp.RecordTest") {
    GIVEN("a Foo record instance") {
        auto foo = test::record::Foo(42);
        WHEN("passing the record through a helper interface") {
            auto new_foo = test::record::Helper::get_foo(foo);
            THEN("the record should still be the same") {
                REQUIRE(new_foo.bar == foo.bar);
                REQUIRE(new_foo.bar == 42);
            }
        }
        THEN("the defined constant should be available") {
            REQUIRE(foo.BAZ == 5);
            REQUIRE(test::record::Foo::BAZ == 5);
        }
    }
}
