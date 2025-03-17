// Copyright 2025 jothepro
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

#include "not_null_interface.hpp"

namespace test::not_null_test {

class NotNullInterfaceImpl : public NotNullInterface {
public:
    void not_null_parameter(const ::gsl::not_null<std::shared_ptr<::test::not_null_test::NotNullInterface>> & param) noexcept override;
    void not_null_function_parameter(const std::function<void()> & param) noexcept override;
    void not_null_string_parameter(const std::string& param) noexcept override;
};

}
