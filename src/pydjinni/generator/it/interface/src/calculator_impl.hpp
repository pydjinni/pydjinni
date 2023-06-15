#pragma once
#include "calculator.hpp"
namespace test::interface {

class CalculatorImpl : public Calculator {
public:
    int8_t add(const int8_t& a, const int8_t& b) override;
};

}