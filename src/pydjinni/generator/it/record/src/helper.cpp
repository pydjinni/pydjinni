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
    return foo;
}

}
