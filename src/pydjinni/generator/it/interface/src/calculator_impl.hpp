// Copyright 2023 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once
#include "calculator.hpp"
namespace test::interface_test {

class CalculatorImpl : public Calculator {
public:
    int8_t add(int8_t a, int8_t b) override;
    int8_t get_platform_value(const std::shared_ptr<PlatformInterface>& platform) override;
    void no_parameters_no_return() override;
    void throwing_exception() override;
};

}
