#include "optional_interface.hpp"
#include "optional_interface_impl.hpp"

using namespace test::interface_test;

std::shared_ptr<::test::interface_test::OptionalInterface> OptionalInterface::get_instance() noexcept {
    return std::make_shared<OptionalInterfaceImpl>();
}

std::shared_ptr<::test::interface_test::OptionalInterface> OptionalInterface::get_null_instance() noexcept {
    return nullptr;
}
