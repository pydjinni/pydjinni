#include "helper.hpp"
#include <cassert>

namespace test::record {

Foo Helper::get_foo(const Foo& foo) {
    assert(foo.boolean_t == true);
    assert(foo.byte_t == 8);
    assert(foo.short_t == 16);
    assert(foo.int_t == 32);
    assert(foo.long_t == 64);
    assert(foo.float_t > 32 && foo.float_t < 33);
    assert(foo.double_t > 64 && foo.double_t < 65);
    assert(foo.string_t == "test string");
    assert(foo.int_list.size() == 2);
    assert(foo.int_list[0] == 0);
    assert(foo.int_list[1] == 1);
    assert(foo.string_list.size() == 2);
    assert(foo.string_list[0] == "foo");
    assert(foo.string_list[1] == "bar");
    assert(foo.int_optional.has_value());
    assert(foo.int_optional.value() == 42);
    assert(foo.string_optional.has_value());
    assert(foo.string_optional.value() == "optional");
    return foo;
}

}
