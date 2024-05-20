//
// Copyright 2024 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once
#include <coroutine>
#include <functional>

namespace pydjinni {

// Generic Awaitable class
template<typename T>
class awaitable {
public:
    explicit awaitable(std::function<void(std::function < void(T) > )> async_func)
            : async_func_(std::move(async_func)) {}

    [[nodiscard]] bool await_ready() const noexcept { return false; }
    T await_resume() noexcept { return result_; }

    void await_suspend(std::coroutine_handle<> handle) {
        async_func_([this, handle](T result) {
            result_ = result;
            handle.resume();
        });
    }

private:
    std::function<void(std::function < void(T) > )> async_func_;
    T result_;
};

// Specialization for void return type
template<>
class awaitable<void> {
public:
    explicit awaitable(std::function<void(std::function < void() > )> async_func)
            : async_func_(std::move(async_func)) {}

    static bool await_ready() noexcept { return false; }

    void await_resume() noexcept {}

    void await_suspend(std::coroutine_handle<> handle) {
        async_func_([this, handle] {
            handle.resume();
        });
    }

private:
    std::function<void(std::function <void()>)> async_func_;
};

// Helper function to create a generic awaitable
template<typename T>
auto make_awaitable(std::function<void(std::function < void(T) > )> async_func) {
    return awaitable<T>(std::move(async_func));
}

}
