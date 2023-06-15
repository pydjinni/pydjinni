#include "calculator.hpp"
#include "calculator_impl.hpp"

using namespace test::interface;

std::shared_ptr<Calculator> Calculator::get_instance() {
    return std::make_shared<CalculatorImpl>();
}

