#include "calculator_impl.hpp"

using namespace test::interface;

int8_t CalculatorImpl::add(const int8_t& a, const int8_t& b) {
    return a + b;
}

int8_t CalculatorImpl::get_platform_value(const std::shared_ptr<PlatformInterface>& platform) {
    auto val =  platform->get_value();
    assert(val == 5);
    return val;
}