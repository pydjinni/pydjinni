#pragma once
#include "calculator.hpp"
namespace test::interface {

class CalculatorImpl : public Calculator {
public:
    int8_t add(const int8_t& a, const int8_t& b) override;
    int8_t get_platform_value(const std::shared_ptr<PlatformInterface>& platform) override;
};

}