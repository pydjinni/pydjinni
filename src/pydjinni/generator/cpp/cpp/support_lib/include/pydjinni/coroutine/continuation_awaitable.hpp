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
#include <utility>
#include "continuation_runner.hpp"

namespace pydjinni::coroutine {
    struct ContinuationAwaitable {
        bool await_ready() const noexcept { return false; }
        void await_suspend(std::coroutine_handle<> handle) noexcept {
            scheduler_({continuation_, handle});
        }
        void await_resume() const noexcept {}

        std::coroutine_handle<> continuation_;
        std::function<void(const pydjinni::coroutine::ContinuationRunner &runner)> scheduler_;
    };
}


