#include "calculator_impl.hpp"
#include <cassert>
#include <stdexcept>

using namespace test::interface;

int8_t CalculatorImpl::add(int8_t a, int8_t b) {
    return a + b;
}

int8_t CalculatorImpl::get_platform_value(const std::shared_ptr<PlatformInterface>& platform) {
    auto val =  platform->get_value();
    assert(val == 5);
    return val;
}

void CalculatorImpl::no_parameters_no_return() {}

void CalculatorImpl::throwing_exception() {
    throw std::runtime_error("shit hit the fan");
}

void CalculatorImpl::update_readonly_property(int32_t value) {
    _readonly_value = value;
}
