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
#include <coroutine>
#include <exception>
#include <functional>

namespace pydjinni::coroutine {
    template<typename T = void>
    struct CallbackHandle {
        template <std::convertible_to<T> Arg>
        void resume(Arg&& result) noexcept {
            result_ = std::forward<Arg>(result);
            continuation_.resume();
        }
        void error(const std::exception_ptr& exception) noexcept {
            exception_ = exception;
            continuation_.resume();
        }
        T result() const {
            if(exception_) std::rethrow_exception(exception_);
            return result_;
        }
        std::coroutine_handle<> continuation_;
        T result_ = {};
        std::exception_ptr exception_ = nullptr;
    };

    template<>
    struct CallbackHandle<void> {
        void resume() const noexcept {
            continuation_.resume();
        }
        void error(const std::exception_ptr& exception) noexcept {
            exception_ = exception;
            continuation_.resume();
        }
        void result() const {
            if(exception_) std::rethrow_exception(exception_);
        }
        std::coroutine_handle<> continuation_;
        std::exception_ptr exception_ = nullptr;
    };

    template<typename T = void>
    struct CallbackAwaitable {

        bool await_ready() const noexcept { return false; }
        void await_suspend(std::coroutine_handle<> handle) noexcept {
            handle_ = CallbackHandle<T>{handle};
            callback_(handle_);
        }
        T await_resume() const {
            return handle_.result();
        }
        std::function<void(CallbackHandle<T>& handle)> callback_;
        CallbackHandle<T> handle_;
    };
}
