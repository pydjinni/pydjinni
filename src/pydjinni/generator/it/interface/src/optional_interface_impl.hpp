#pragma once
#include "optional_interface.hpp"

namespace test::interface_test {
    class OptionalInterfaceImpl : public OptionalInterface {
        std::optional<std::string> optional_parameter(const std::optional<std::string> & param) noexcept override;
        std::optional<std::string> optional_null_parameter(const std::optional<std::string> & param) noexcept override;
    };
}
