#include "optional_interface_impl.hpp"
#include <cassert>

using namespace test::interface_test;

std::optional<std::string> OptionalInterfaceImpl::optional_parameter(const std::optional<std::string> &param) noexcept {
    assert(param.has_value());
    assert(param.value() == "some optional string");
    return param;
}

std::optional<std::string>
OptionalInterfaceImpl::optional_null_parameter(const std::optional<std::string> &param) noexcept {
    assert(!param.has_value());
    return param;
}
