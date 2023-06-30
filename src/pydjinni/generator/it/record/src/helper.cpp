#include "helper.hpp"
#include <cassert>

namespace test::record {

PrimitiveTypes Helper::get_primitive_types(const ::test::record::PrimitiveTypes &record) {
    assert(record.boolean_t == true);
    assert(record.byte_t == 8);
    assert(record.short_t == 16);
    assert(record.int_t == 32);
    assert(record.long_t == 64);
    assert(record.float_t > 32 && record.float_t < 33);
    assert(record.double_t > 64 && record.double_t < 65);
    assert(record.string_t == "test string");
    return record;
}

CollectionTypes Helper::get_collection_types(const ::test::record::CollectionTypes &record) {
    assert(record.int_list.size() == 2);
    assert(record.int_list[0] == 0);
    assert(record.int_list[1] == 1);
    assert(record.string_list.size() == 2);
    assert(record.string_list[0] == "foo");
    assert(record.string_list[1] == "bar");
    assert(record.int_set.size() == 2);
    assert(record.int_set.contains(0));
    assert(record.int_set.contains(1));
    assert(record.string_set.size() == 2);
    assert(record.string_set.contains("foo"));
    assert(record.string_set.contains("bar"));
    return record;
}

OptionalTypes Helper::get_optional_types(const ::test::record::OptionalTypes &record) {
    assert(record.int_optional.has_value());
    assert(record.int_optional.value() == 42);
    assert(record.string_optional.has_value());
    assert(record.string_optional.value() == "optional");
    return record;
}

}
