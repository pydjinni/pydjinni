#include "helper.hpp"
#include <cassert>

using namespace test::enum_test;

ExampleEnum Helper::get_enum(ExampleEnum example_enum) {
    assert(example_enum == ExampleEnum::A);
    return example_enum;
}
