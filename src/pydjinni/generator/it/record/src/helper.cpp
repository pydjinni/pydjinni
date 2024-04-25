// Copyright 2023 - 2024 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "helper.hpp"
#include "base_record.hpp"
#include <cassert>

namespace test::record {

PrimitiveTypes Helper::get_primitive_types(const PrimitiveTypes &record_type) noexcept {
    assert(record_type.boolean_t == true);
    assert(record_type.byte_t == 8);
    assert(record_type.short_t == 16);
    assert(record_type.int_t == 32);
    assert(record_type.long_t == 64);
    assert(record_type.float_t > 32 && record_type.float_t < 33);
    assert(record_type.double_t > 64 && record_type.double_t < 65);
    assert(record_type.string_t == "test string");
    assert(record_type.date_t == std::chrono::time_point<std::chrono::system_clock>(std::chrono::seconds(1688213309)));
    return record_type;
}

CollectionTypes Helper::get_collection_types(const CollectionTypes &record_type) noexcept {
    assert(record_type.int_list.size() == 2);
    assert(record_type.int_list[0] == 0);
    assert(record_type.int_list[1] == 1);

    assert(record_type.string_list.size() == 2);
    assert(record_type.string_list[0] == "foo");
    assert(record_type.string_list[1] == "bar");

    assert(record_type.int_set.size() == 2);
    assert(record_type.int_set.contains(0));
    assert(record_type.int_set.contains(1));

    assert(record_type.string_set.size() == 2);
    assert(record_type.string_set.contains("foo"));
    assert(record_type.string_set.contains("bar"));

    assert(record_type.int_int_map.size() == 1);
    assert(record_type.int_int_map.at(0) == 1);

    assert(record_type.string_string_map.size() == 1);
    assert(record_type.string_string_map.at("foo") == "bar");

    return record_type;
}

OptionalTypes Helper::get_optional_types(const OptionalTypes &record_type) noexcept {
    assert(record_type.int_optional.has_value());
    assert(record_type.int_optional.value() == 42);
    assert(record_type.string_optional.has_value());
    assert(record_type.string_optional.value() == "optional");
    return record_type;
}

BinaryTypes Helper::get_binary_types(const BinaryTypes &record_type) noexcept {
    assert(record_type.binary_t.size() == 1);
    assert(record_type.binary_t == std::vector<uint8_t>{0x8F});
    return record_type;
}

BaseRecord Helper::get_cpp_base_record() noexcept {
    return {};
}

BaseRecord Helper::get_host_base_record(const BaseRecord &record_type) noexcept {
    assert(record_type.value == 42);
    return record_type;
}

ParentType Helper::get_nested_type(const ::test::record::ParentType &parent) noexcept {
    assert(parent.nested.a == 42);
    return parent;
}

}
