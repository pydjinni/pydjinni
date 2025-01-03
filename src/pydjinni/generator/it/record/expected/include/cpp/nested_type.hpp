// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
#pragma once
#include <algorithm>
#include <cstdint>
#include <format>
#include <vector>

namespace test::record {
struct NestedType final {
    const int32_t a;
    const std::vector<std::vector<int32_t>> b;
    NestedType(int32_t a, std::vector<std::vector<int32_t>> b)
    : a(std::move(a))
    , b(std::move(b))
    {}
};
std::string to_string(const ::test::record::NestedType& value);
} // namespace test::record
template<>
struct std::formatter<::test::record::NestedType> : std::formatter<std::string> {
    template<typename FormatContext>
    auto format(const ::test::record::NestedType& value, FormatContext &ctx) const {
        return std::format_to(ctx.out(), "{}", test::record::to_string(value));
    }
};
