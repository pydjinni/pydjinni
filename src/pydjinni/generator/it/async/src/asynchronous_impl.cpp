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

#include <stdexcept>
#include "asynchronous_impl.hpp"

using namespace test::async_test;

pydjinni::coroutine::task<int32_t> AsynchronousImpl::add(int32_t a, int32_t b) noexcept {
    co_return a + b;
}

pydjinni::coroutine::task<> AsynchronousImpl::no_parameters_no_return() noexcept {
    co_return;
}

pydjinni::coroutine::task<> AsynchronousImpl::throwing_exception() {
    throw std::runtime_error("asynchronous runtime error");
    co_return;
}

pydjinni::coroutine::task<int32_t> AsynchronousImpl::multiply_callback(const std::shared_ptr<::test::async_test::MultiplyCallback> &callback) noexcept {
    auto result = co_await callback->invoke(21, 2);
    co_return result;
}

pydjinni::coroutine::task<> AsynchronousImpl::no_parameters_no_return_callback(const std::shared_ptr<::test::async_test::NoParametersNoReturnCallback> &callback) noexcept {
    co_await callback->invoke();
}

pydjinni::coroutine::task<> AsynchronousImpl::throwing_callback(const std::shared_ptr<::test::async_test::ThrowingCallback> &callback) {
    co_await callback->invoke();
}

