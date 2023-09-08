#pragma once
#include "calculator.hpp"
namespace test::interface {

class CalculatorImpl : public Calculator {
public:
    int8_t add(int8_t a, int8_t b) override;
    int8_t get_platform_value(const std::shared_ptr<PlatformInterface>& platform) override;
    void no_parameters_no_return() override;
    void throwing_exception() override;
    void update_readonly_property(int32_t value) override;
};

}