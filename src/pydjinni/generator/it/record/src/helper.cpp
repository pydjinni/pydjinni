#include "helper.hpp"

namespace test::record {

Foo Helper::get_foo(const Foo& foo) {
    assert(foo.bar == 42);
    return foo;
}

}
