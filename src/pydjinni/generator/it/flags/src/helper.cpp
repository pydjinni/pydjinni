#include "helper.hpp"
#include <cassert>

using namespace test::flags_test;

ExampleFlags Helper::get_flag(ExampleFlags example_flag) {
    assert(example_flag == ExampleFlags::A);
    return example_flag;
}

ExampleFlags Helper::get_all_flag(ExampleFlags example_flag) {
    assert(example_flag == ((ExampleFlags)0 | ExampleFlags::A | ExampleFlags::B)); // ExampleFlags::ALL
    return example_flag;
}

ExampleFlags Helper::get_none_flag(ExampleFlags example_flag) {
    assert(example_flag == (ExampleFlags)0); // ExampleFlags::NONE
    return example_flag;
}

