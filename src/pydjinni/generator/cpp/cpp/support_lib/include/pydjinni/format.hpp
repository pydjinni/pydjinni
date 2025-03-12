#pragma once
#include <format>
#include <string>
#include <optional>

namespace pydjinni {

template<typename T>
auto format(const std::optional<T>& value) {
    if constexpr (std::formattable<T, char>) return value.has_value() ? std::format("{}", value.value()) : "null";
    else return "{?}";
}

template<typename T>
auto format(const T& value)
{
    if constexpr (std::formattable<T, char>) return value;
    else return "{?}";
}

}
