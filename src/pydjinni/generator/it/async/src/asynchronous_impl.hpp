// Copyright 2024 jothepro
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
#include "asynchronous.hpp"

namespace test::async_test {
    class AsynchronousImpl : public Asynchronous {
        pydjinni::coroutine::task<int32_t> add(int32_t a, int32_t b) noexcept override;
        pydjinni::coroutine::task<> no_parameters_no_return() noexcept override;
        pydjinni::coroutine::task<> throwing_exception() override;
        pydjinni::coroutine::task<int32_t> multiply_callback(const std::shared_ptr<::test::async_test::MultiplyCallback> & callback) noexcept override;
        pydjinni::coroutine::task<> no_parameters_no_return_callback(const std::shared_ptr<::test::async_test::NoParametersNoReturnCallback>& callback) noexcept override;
        pydjinni::coroutine::task<> throwing_callback(const std::shared_ptr<::test::async_test::ThrowingCallback>& callback) override;
    };
}
