// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
#pragma once
#include <algorithm>
#include <ostream>
#include <iomanip>
#include <version>
#ifdef __cpp_lib_format
#include <format>
#endif
#include <cstdint>
#include <string>
#include <chrono>

namespace test::record {
struct PrimitiveTypes final {
    const bool boolean_t;
    const int8_t byte_t;
    const int16_t short_t;
    const int32_t int_t;
    const int64_t long_t;
    const float float_t;
    const double double_t;
    const std::string string_t;
    const std::chrono::system_clock::time_point date_t;
    PrimitiveTypes(bool boolean_t_, int8_t byte_t_, int16_t short_t_, int32_t int_t_, int64_t long_t_, float float_t_, double double_t_, std::string string_t_, std::chrono::system_clock::time_point date_t_)
    : boolean_t(std::move(boolean_t_))
    , byte_t(std::move(byte_t_))
    , short_t(std::move(short_t_))
    , int_t(std::move(int_t_))
    , long_t(std::move(long_t_))
    , float_t(std::move(float_t_))
    , double_t(std::move(double_t_))
    , string_t(std::move(string_t_))
    , date_t(std::move(date_t_))
    {}

    friend bool operator==(const PrimitiveTypes& lhs, const PrimitiveTypes& rhs);
    friend bool operator!=(const PrimitiveTypes& lhs, const PrimitiveTypes& rhs);
    friend std::ostream& operator<<(std::ostream& os, PrimitiveTypes const& value);
};
}  // namespace test::record
