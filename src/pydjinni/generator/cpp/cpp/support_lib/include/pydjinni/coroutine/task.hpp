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
#include <utility>
#include "continuation_awaitable.hpp"

namespace pydjinni::coroutine {
    template <typename T = void>
    struct task {
        struct promise_type {
            using handle_t = std::coroutine_handle<promise_type>;
            // Get the caller access to the handle
            task get_return_object() {
                return task{handle_t::from_promise(*this)};
            }

            std::suspend_always initial_suspend() const noexcept { return {}; }
            ContinuationAwaitable final_suspend() const noexcept {
                return { continuation_, scheduler_ };
            }

            template<typename U>
            task<U> await_transform(task<U>&& awaitable) {
                awaitable.set_scheduler(scheduler_);
                return awaitable;
            }

            template<typename OtherAwaitable>
            OtherAwaitable await_transform(OtherAwaitable&& awaitable) {
                return awaitable;
            }

            template <std::convertible_to<T> Arg>
            void return_value(Arg&& result) noexcept {
                result_ = std::forward<Arg>(result);
                if(callback_) callback_(result_);
            }
            void unhandled_exception() noexcept {
                exception_ = std::current_exception();
                if(error_callback_) error_callback_(exception_);
            }

            T result() {
                if(exception_) std::rethrow_exception(exception_);
                return result_;
            }

            std::coroutine_handle<> continuation_{std::noop_coroutine()};
            T result_;
            std::exception_ptr exception_ = nullptr;
            std::function<void(T)> callback_ = nullptr;
            std::function<void(const std::exception_ptr&)> error_callback_ = nullptr;
            std::function<void(const pydjinni::coroutine::ContinuationRunner &runner)> scheduler_ = nullptr;
        };

        // Store the coroutine handle
        explicit task(std::coroutine_handle<promise_type> handle)
                : handle_(handle) {}

        // Awaitable interface
        bool await_ready() noexcept { return false; }
        // When we await on the result of calling a coroutine
        // the coroutine will start, but will also remember its caller
        std::coroutine_handle<> await_suspend(std::coroutine_handle<> caller) noexcept {
            // Remember the caller
            handle_.promise().continuation_ = caller;
            // Returning a coroutine handle will run the corresponding coroutine
            return handle_;
        }
        T await_resume() const {
            return handle_.promise().result();
        }

        void run(std::function<void(const pydjinni::coroutine::ContinuationRunner &runner)> scheduler) {
            set_scheduler(scheduler);
            handle_();
        }

        task<T>& on_success(const std::function<void(T)>& callback) {
            handle_.promise().callback_ = callback;
            return *this;
        }

        task<T>& on_error(const std::function<void(const std::exception_ptr&)>& error_callback) {
            handle_.promise().error_callback_ = error_callback;
            return *this;
        }

    private:
        void set_scheduler(std::function<void(const pydjinni::coroutine::ContinuationRunner &runner)> scheduler) {
            handle_.promise().scheduler_ = scheduler;
        }

        std::coroutine_handle<promise_type> handle_;

        template <typename U>
        friend struct task;

    };


    template<>
    struct task<void> {
        struct promise_type {
            using handle_t = std::coroutine_handle<promise_type>;
            // Get the caller access to the handle
            task get_return_object() {
                return task{handle_t::from_promise(*this)};
            }

            std::suspend_always initial_suspend() const noexcept { return {}; }
            ContinuationAwaitable final_suspend() const noexcept {
                return { continuation_, scheduler_ };
            }

            template<typename U>
            task<U> await_transform(task<U>&& awaitable) {
                awaitable.set_scheduler(scheduler_);
                return awaitable;
            }

            template<typename OtherAwaitable>
            OtherAwaitable await_transform(OtherAwaitable&& awaitable) {
                return awaitable;
            }

            void return_void() const noexcept {
                if(callback_) callback_();
            }
            void unhandled_exception() noexcept {
                exception_ = std::current_exception();
                if(error_callback_) error_callback_(exception_);
            }

            void result() {
                if(exception_) std::rethrow_exception(exception_);
            }

            std::coroutine_handle<> continuation_{std::noop_coroutine()};
            std::exception_ptr exception_ = nullptr;
            std::function<void()> callback_ = nullptr;
            std::function<void(const std::exception_ptr&)> error_callback_ = nullptr;
            std::function<void(const pydjinni::coroutine::ContinuationRunner &runner)> scheduler_ = nullptr;
        };

        // Store the coroutine handle
        explicit task(std::coroutine_handle<promise_type> handle)
                : handle_(handle) {}

        // Awaitable interface
        bool await_ready() const noexcept { return false; }
        // When we await on the result of calling a coroutine
        // the coroutine will start, but will also remember its caller
        std::coroutine_handle<> await_suspend(std::coroutine_handle<> caller) noexcept {
            // Remember the caller
            handle_.promise().continuation_ = caller;
            // Returning a coroutine handle will run the corresponding coroutine
            return handle_;
        }
        void await_resume() const {
            return handle_.promise().result();
        }

        void run(std::function<void(const pydjinni::coroutine::ContinuationRunner &runner)> scheduler) {
            set_scheduler(scheduler);
            handle_.resume();
        }

        task<void>& on_success(const std::function<void()>& callback) {
            handle_.promise().callback_ = callback;
            return *this;
        }

        task<void>& on_error(const std::function<void(const std::exception_ptr&)>& error_callback) {
            handle_.promise().error_callback_ = error_callback;
            return *this;
        }

    private:
        void set_scheduler(std::function<void(const pydjinni::coroutine::ContinuationRunner &runner)> scheduler) {
            handle_.promise().scheduler_ = scheduler;
        }

        std::coroutine_handle<promise_type> handle_;

        template <typename U>
        friend struct task;
    };
}
