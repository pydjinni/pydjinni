// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'flags.pydjinni'
#pragma once
#include <format>

namespace test::flags_test {
enum class ExampleFlags : unsigned {
    A = 1u << 0,
    B = 1u << 1,
    ALL = 0 | A | B,
    NONE = 0
};

constexpr ExampleFlags operator|(ExampleFlags lhs, ExampleFlags rhs) noexcept {
    return static_cast<::test::flags_test::ExampleFlags>(static_cast<unsigned>(lhs) | static_cast<unsigned>(rhs));
}
inline ExampleFlags& operator|=(ExampleFlags& lhs, ExampleFlags rhs) noexcept {
    return lhs = lhs | rhs;
}
constexpr ExampleFlags operator&(ExampleFlags lhs, ExampleFlags rhs) noexcept {
    return static_cast<ExampleFlags>(static_cast<unsigned>(lhs) & static_cast<unsigned>(rhs));
}
inline ExampleFlags& operator&=(ExampleFlags& lhs, ExampleFlags rhs) noexcept {
    return lhs = lhs & rhs;
}
constexpr ExampleFlags operator^(ExampleFlags lhs, ExampleFlags rhs) noexcept {
    return static_cast<ExampleFlags>(static_cast<unsigned>(lhs) ^ static_cast<unsigned>(rhs));
}
inline ExampleFlags& operator^=(ExampleFlags& lhs, ExampleFlags rhs) noexcept {
    return lhs = lhs ^ rhs;
}
constexpr ExampleFlags operator~(ExampleFlags x) noexcept {
    return static_cast<ExampleFlags>(~static_cast<unsigned>(x));
}
std::string to_string(::test::flags_test::ExampleFlags value) noexcept;
} // namespace test::flags_test
template<>
struct std::formatter<::test::flags_test::ExampleFlags> : std::formatter<std::string> {
    template<typename FormatContext>
    auto format(test::flags_test::ExampleFlags value, FormatContext &ctx) const {
        return std::format_to(ctx.out(), "{}", test::flags_test::to_string(value));
    }
};
