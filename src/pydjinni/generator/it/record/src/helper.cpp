#include "helper.hpp"
#include <cassert>

namespace test::record {

Foo Helper::get_foo(const Foo& foo) {
    assert(foo.bar == 42);
    return foo;
}

}
