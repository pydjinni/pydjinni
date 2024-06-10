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

namespace coroutine {
    template<class T>
    struct task {
        struct promise_type {
            T value_;
            using Handle = std::coroutine_handle<promise_type>;
            task get_return_object() {
                return task{Handle::from_promise(*this)};
            }
            std::suspend_always initial_suspend() { return {}; }
            std::suspend_always final_suspend() noexcept { return {}; }
            void return_value(T value) {
                value_ = value;
            }
            void unhandled_exception() { }
        };
        explicit task(promise_type::Handle coro) : coro_(coro) {}

        [[nodiscard]] bool await_ready() const noexcept { return false; }

        static void await_suspend(std::coroutine_handle<> handle) {
            handle.resume();
        }

        T await_resume() noexcept {
            coro_.resume();
            return coro_.promise().value_;
        }
    private:
        promise_type::Handle coro_;
    };

    template<>
    struct task<void> {
        // The coroutine level type
        struct promise_type {
            using Handle = std::coroutine_handle<promise_type>;
            task get_return_object() {
                return task{Handle::from_promise(*this)};
            }
            static std::suspend_always initial_suspend() { return {}; }
            static std::suspend_always final_suspend() noexcept { return {}; }
            void return_void() {}
            void unhandled_exception() { }
        };
        explicit task(promise_type::Handle coro) : coro_(coro) {}

        [[nodiscard]] bool await_ready() const noexcept { return false; }

        static void await_suspend(std::coroutine_handle<> handle) {
            handle.resume();
        }

        void await_resume() noexcept {
            coro_.resume();
        }
    private:
        promise_type::Handle coro_;
    };

    template<class T>
    T run_blocking(task<T> task) {
        return task.await_resume();
    }
}
